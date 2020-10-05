import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import os, time, datetime
import process_data, setting


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def eval_model(dataset, model, criterion, epoch_num):
    # デバイスの指定
    model.to(device)

    # dataloaderの作成
    dataloader = DataLoader(dataset, batch_size=setting.BATCH_SIZE, shuffle=True)

    start = time.time()
    epoch_loss = 0
    model.eval()
    i=1

    with torch.no_grad():
        for data in dataloader:
            # デバイスの指定
            src_ids = data['src_ids'].to(device)
            trg_ids = data['trg_ids'].to(device)
            # src_mask = data['src_mask'].to(device)
            # trg_mask = data['trg_mask'].to(device)

            batch = process_data.Batch(src_ids, trg_ids, pad=0)  # モデルの入力に合わせてバッチを加工
        
            outputs = model.forward(batch.src, batch.trg, batch.src_mask, batch.trg_mask)  # 学習
        
            loss = criterion(outputs.contiguous().view(-1, outputs.size(-1)), batch.trg_y.contiguous().view(-1)) / batch.ntokens
            epoch_loss += loss

            # if i % 10 == 0:
            #     print("{:.1f}%完了".format(i / len(dataloader) * 100))
            #     print(loss)
            #     print(epoch_loss / (i))

            i+=1


    elapsed = time.time() - start
    # 進捗状況の表示
    print("Epoch: {}; Percent complete: {:.1f}%; loss: {:.4f}, {}sec, {}".format(epoch_num, epoch_num / setting.MAX_EPOCH_NUM * 100, epoch_loss / (i - 1), elapsed, datetime.datetime.now()))
    with open("eval_log.txt", "a", encoding="utf-8") as logFile:
        logFile.write("Epoch: {}; Percent complete: {:.1f}%; loss: {:.4f}, {}sec, {}\n".format(epoch_num, epoch_num / setting.MAX_EPOCH_NUM * 100, epoch_loss / (i - 1), elapsed, datetime.datetime.now()))
