import torch
import numpy as np
from transformers import BertTokenizer
import model_manager, process_data, setting


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def subsequent_mask(size):
    "Mask out subsequent positions."
    attn_shape = (1, size, size)
    subsequent_mask = np.triu(np.ones(attn_shape), k=1).astype('uint8')
    return torch.from_numpy(subsequent_mask) == 0


# 入力分を受け取って、返事を作成する。
def make_reply(input_sentence, model, tokenizer):
    ids = tokenizer.encode_plus(input_sentence, add_special_tokens=True, max_length=setting.MAX_SENTENCE_LENGTH * 2, pad_to_max_length=True, truncation=True)

    ids = torch.tensor([ids["input_ids"]]).to(device)

    ids_and_mask = process_data.Batch(ids)
    ids = ids_and_mask.src
    mask = ids_and_mask.src_mask

    memory = model.encode(ids, mask)
    ys = torch.ones(1, 1).fill_(tokenizer.cls_token_id).long().to(device)

    for i in range(setting.MAX_SENTENCE_LENGTH * 2 - 1):
        out = model.decode(memory, mask, ys, subsequent_mask(ys.size(1)).type_as(ys))
        prob = model.generator(out[:, -1])
        _, next_word = torch.max(prob, dim = 1)
        next_word = next_word.data[0]
        ys = torch.cat([ys, torch.ones(1, 1).type_as(ys).fill_(next_word)], dim=1)

    ys = ys.view(-1).detach().cpu().numpy().tolist()[1:]
    text = tokenizer.decode(ys, skip_special_tokens = True, clean_up_tokenization_spaces=True)

    return text.replace(' ', '')


if __name__ == "__main__":
    tokenizer = BertTokenizer.from_pretrained('cl-tohoku/bert-base-japanese-whole-word-masking')
    model, _, _, _ = model_manager.get_model(True, tokenizer)
    model = model.to(device)
    model.eval()

    while True:
        input_sentence = input('> ')
        if input_sentence == 'q' or input_sentence == 'quit': break

        reply = make_reply(input_sentence, model, tokenizer)
        print("BOT : " + reply)