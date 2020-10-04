import time
import torch
from torch.utils.data import Dataset
from transformers import BertTokenizer
import database_manager, model_manager, model_eval, setting


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
    database = database_manager.load_database(setting.EVAL_DATABASE_SAVE_FILE_NAME)  # コーパスデータ取り出し   

    tokenizer = BertTokenizer.from_pretrained('cl-tohoku/bert-base-japanese-whole-word-masking')
    dataset = CreateDataset(database.pairs, tokenizer, setting.MAX_SENTENCE_LENGTH * 2)

    for var in dataset[0]:
        print(f'{var}: {dataset[0][var]}')


    for epoch_num in range(1, setting.LOAD_MODEL_EPOCH_NUM+1):
        model, _, criterion, epoch_num = model_manager.get_model(True, tokenizer, epoch_num)  # モデルの取得。

        model_eval.eval_model(dataset, model, criterion, epoch_num)    # モデルの評価