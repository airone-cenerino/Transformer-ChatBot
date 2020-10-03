import time
import torch
from torch.utils.data import Dataset
from transformers import BertTokenizer
import database_manager, model_manager, model_training, setting


class CreateDataset(Dataset):
    def __init__(self, sentence_pair, tokenizer, max_len):
        self.sentence_pair = sentence_pair
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __getitem__(self, idx):
        src, trg = self.sentence_pair[idx]
        src = self.tokenizer.encode_plus(src, add_special_tokens=True, max_length=self.max_len, pad_to_max_length=True, truncation=True)
        trg = self.tokenizer.encode_plus(trg, add_special_tokens=True, max_length=self.max_len, pad_to_max_length=True, truncation=True)

        src_ids = src['input_ids']
        # src_mask = src['attention_mask']
        trg_ids = trg['input_ids']
        # trg_mask = trg['attention_mask']

        return {
        'src_ids': torch.LongTensor(src_ids),
        # 'src_mask': torch.LongTensor(src_mask),
        'trg_ids': torch.LongTensor(trg_ids),
        # 'trg_mask': torch.LongTensor(trg_mask),
        }

    def __len__(self):
        return len(self.sentence_pair)


if __name__ == "__main__":
    database = database_manager.load_database()  # コーパスデータ取り出し
    

    tokenizer = BertTokenizer.from_pretrained('cl-tohoku/bert-base-japanese-whole-word-masking')
    dataset = CreateDataset(database.pairs, tokenizer, setting.MAX_SENTENCE_LENGTH * 2)

    for var in dataset[0]:
        print(f'{var}: {dataset[0][var]}')


    model, optimizer, criterion, epoch_num = model_manager.get_model(setting.IS_TRAIN_FROM_THE_MIDDLE, tokenizer)  # モデルの取得。
    optimizer.optimizer._step = int(epoch_num * database.pair_num /setting.BATCH_SIZE) # optimizerのLearningRateが途中から学習の際に初めからにならないようにする。

    model_training.train_iters(dataset, model, criterion, optimizer, epoch_num)    # トレーニング開始