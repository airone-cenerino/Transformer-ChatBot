import copy
import torch
import torch.nn as nn
import os
import network_model, setting


class LabelSmoothing(torch.nn.Module):
    "Implement label smoothing."
    def __init__(self, size, padding_idx, smoothing=0.0):
        super(LabelSmoothing, self).__init__()
        self.criterion = torch.nn.KLDivLoss(size_average=False)
        self.padding_idx = padding_idx
        self.confidence = 1.0 - smoothing
        self.smoothing = smoothing
        self.size = size
        self.true_dist = None
        
    def forward(self, x, target):
        assert x.size(1) == self.size
        true_dist = x.data.clone()
        true_dist.fill_(self.smoothing / (self.size - 2))
        true_dist.scatter_(1, target.data.unsqueeze(1), self.confidence)
        true_dist[:, self.padding_idx] = 0
        mask = torch.nonzero(target.data == self.padding_idx)
        if mask.dim() > 0:
            true_dist.index_fill_(0, mask.squeeze(), 0.0)
        self.true_dist = true_dist

        return self.criterion(x, torch.autograd.Variable(true_dist, requires_grad=False))

        
class NoamOpt:
    "Optim wrapper that implements rate."
    def __init__(self, model_size, factor, warmup, optimizer):
        self.optimizer = optimizer
        self._step = 0
        self.warmup = warmup
        self.factor = factor
        self.model_size = model_size
        self._rate = 0
        
    def step(self):
        "Update parameters and rate"
        self._step += 1
        rate = self.rate()
        for p in self.optimizer.param_groups:
            p['lr'] = rate
        self._rate = rate
        self.optimizer.step()
        
    def rate(self, step = None):
        "Implement `lrate` above"
        if step is None:
            step = self._step
        return self.factor * \
            (self.model_size ** (-0.5) *
            min(step ** (-0.5), step * self.warmup ** (-1.5)))


# モデルの作成
def make_model(vocab_size, N=6, d_model=setting.EMBEDDING_DIM, d_ff=2048, h=8, dropout=0.1):
    c = copy.deepcopy
    attn = network_model.MultiHeadedAttention(h, d_model)
    ff = network_model.PositionwiseFeedForward(d_model, d_ff, dropout)
    position = network_model.PositionalEncoding(d_model, dropout)

    model = network_model.EncoderDecoder(
        network_model.Encoder(network_model.EncoderLayer(d_model, c(attn), c(ff), dropout), N),
        network_model.Decoder(network_model.DecoderLayer(d_model, c(attn), c(attn), c(ff), dropout), N),
        nn.Sequential(network_model.Embeddings(d_model, vocab_size), c(position)),
        nn.Sequential(network_model.Embeddings(d_model, vocab_size), c(position)),
        network_model.Generator(d_model, vocab_size))
    
    # This was important from their code. 
    # Initialize parameters with Glorot / fan_avg.
    for p in model.parameters():
        if p.dim() > 1:
            nn.init.xavier_uniform(p)
    return model


# チェックポイントでセーブされた学習済みモデルのデータをロードする。
def load_checkpoint(epoch_num):
    checkpoint = torch.load(os.path.join(setting.MODEL_SAVE_DIR, '{}_{}.tar'.format(epoch_num, 'epoch')))
    #checkpoint = torch.load(os.path.join(setting.MODEL_SAVE_DIR, '{}_{}.tar'.format(epoch_num, 'epoch')), map_location=torch.device('cpu'))    # GPUのモデルをCPUに移すときはこれを使う。

    model_sd = checkpoint['model']
    optimizer_sd = checkpoint['opt']
    
    return model_sd, optimizer_sd


import matplotlib.pyplot as plt
import numpy as np

# モデル・optimizerを作成 or ロードして返す。
def get_model(is_load_model, tokenizer, epoch_num=setting.LOAD_MODEL_EPOCH_NUM):
    model = make_model(tokenizer.vocab_size)

    #optimizer = NoamOpt(model.src_embed[0].d_model, 2, 400, torch.optim.Adam(model.parameters(), lr=0, betas=(0.9, 0.98), eps=1e-9))
    optimizer = NoamOpt(model.src_embed[0].d_model, 1, 2000, torch.optim.AdamW(model.parameters(), lr=0, betas=(0.9, 0.98), eps=1e-9))
    #optimizer =  torch.optim.AdamW(model.parameters(), lr=0.0001, betas=(0.9, 0.98), eps=1e-9)

    # opts = [NoamOpt(model.src_embed[0].d_model, 1, 400, torch.optim.AdamW(model.parameters(), lr=0, betas=(0.9, 0.98), eps=1e-9)), NoamOpt(model.src_embed[0].d_model, 2, 4000, torch.optim.AdamW(model.parameters(), lr=0, betas=(0.9, 0.98), eps=1e-9)), NoamOpt(model.src_embed[0].d_model, 2, 400, torch.optim.AdamW(model.parameters(), lr=0, betas=(0.9, 0.98), eps=1e-9))]
    # plt.plot(np.arange(1, 20000), [[opt.rate(i) for opt in opts] for i in range(1, 20000)])
    # plt.legend(["1:400", "2:4000", "2:400"])
    # plt.show()

    
    
    criterion = LabelSmoothing(size=tokenizer.vocab_size, padding_idx=tokenizer.pad_token_id, smoothing=0.1)#torch.nn.CrossEntropyLoss(reduction='none')
    #criterion = torch.nn.CrossEntropyLoss(reduction='none')

    # ここでロードしてモデルにパラメータを与える。
    if is_load_model:
        model_sd, optimizer_sd = load_checkpoint(epoch_num)
        model.load_state_dict(model_sd)
        optimizer.optimizer.load_state_dict(optimizer_sd)
        print(epoch_num, "epochのモデルをロードしました。")
    else:
        epoch_num=1
    
    
    # If you have cuda, configure cuda to call
    for state in optimizer.optimizer.state.values():
        for k, v in state.items():
            if isinstance(v, torch.Tensor):
                state[k] = v.cuda()

    return model, optimizer, criterion, epoch_num