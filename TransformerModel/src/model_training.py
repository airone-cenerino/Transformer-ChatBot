import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import os, time, datetime
import process_data, setting


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class SimpleLossCompute:
    "A simple loss compute and train function."
    def __init__(self, criterion, opt=None):
        self.criterion = criterion
        self.opt = opt
        
    def __call__(self, x, y, norm):
        loss = self.criterion(x.contiguous().view(-1, x.size(-1)), 
                              y.contiguous().view(-1)) / norm
        loss.backward()
        if self.opt is not None:
            self.opt.step()
            self.opt.optimizer.zero_grad()

        return loss.data



# バッチを受け取って学習を行う。戻り値はloss。
def train_batch(model, criterion, optimizer, src_ids, trg_ids):
    batch = process_data.Batch(src_ids, trg_ids, pad=0)  # モデルの入力に合わせてバッチを加工
    #optimizer.zero_grad()
    outputs = model.forward(batch.src, batch.trg, batch.src_mask, batch.trg_mask)   # 学習

    loss_compute = SimpleLossCompute(criterion, optimizer)
    loss = loss_compute(outputs, batch.trg_y, batch.ntokens)

    #loss = criterion(outputs.contiguous().view(-1, outputs.size(-1)), batch.trg_y.contiguous().view(-1)) / batch.ntokens
    #loss = criterion(outputs.transpose(1, 2), batch.trg_y).mean()


    #loss.backward()
    _ = nn.utils.clip_grad_norm_(model.parameters(), setting.CLIP)    # Clip gradients: gradients are modified in place
    #optimizer.step()

    return loss


# epochループ。
def train_iters(dataset, model, criterion, optimizer, epoch_num):
    # デバイスの指定
    model.to(device)

    # dataloaderの作成
    dataloader = DataLoader(dataset, batch_size=setting.BATCH_SIZE, shuffle=True)

    # 学習
    print('モデルのトレーニングを開始します。')

    # 初期化
    start_epoch = epoch_num + 1

    for epoch in range(start_epoch, setting.MAX_EPOCH_NUM + 1):
        start = time.time()
        epoch_loss = 0

        # 訓練モードに設定
        model.train()
        i=1

        for data in dataloader:
            # デバイスの指定
            src_ids = data['src_ids'].to(device)
            trg_ids = data['trg_ids'].to(device)
            # src_mask = data['src_mask'].to(device)
            # trg_mask = data['trg_mask'].to(device)

            loss = train_batch(model, criterion, optimizer, src_ids, trg_ids)  # バッチを渡して学習させる。
            epoch_loss += loss

            # if i % 500 == 0:
            #     print("{:.1f}%完了".format(i / len(dataloader) * 100))
            #     print(loss)
            #     print(epoch_loss / (i))
                #print("Epoch: {}; Percent complete: {:.1f}%; loss: {:.4f}, {}".format(epoch, epoch / setting.MAX_EPOCH_NUM * 100, epoch_loss / (i), time.time()))

            i+=1


        elapsed = time.time() - start
        # 進捗状況の表示
        print("Epoch: {}; Percent complete: {:.1f}%; loss: {:.4f}, {}sec, {}".format(epoch, epoch / setting.MAX_EPOCH_NUM * 100, epoch_loss / (i-1), elapsed, datetime.datetime.now()))


        # チェックポイントの保存
        if not os.path.exists(setting.MODEL_SAVE_DIR):
            os.makedirs(setting.MODEL_SAVE_DIR)

        torch.save({
            'epoch': epoch,
            'model': model.state_dict(),
            'opt': optimizer.optimizer.state_dict(),
        }, os.path.join(setting.MODEL_SAVE_DIR, '{}_{}.tar'.format(epoch, 'epoch')))