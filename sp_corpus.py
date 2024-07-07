from underthesea import word_tokenize
import os, string, json, re
from tqdm import tqdm
from sentencepiece import SentencePieceTrainer, SentencePieceProcessor

def train_sp_model(input_sentences_file:str,
                   model_prefix:str,
                   max_word_count:int,
                   model_type:str='word', # unigram, bpe, word or char
                   vocab_size:int=8000) -> None:
    

    SentencePieceTrainer.Train(
        input=input_sentences_file,
        model_type=model_type, # unigram, bpe, word or char
        vocab_size=vocab_size,
        model_prefix=f"{model_prefix}_{model_type}",
        bos_id=0,
        eos_id=1,
        pad_id=2,
        unk_id=3,
        bos_piece='<SOS>',
        eos_piece='<EOS>',
        pad_piece='<PAD>',
        unk_piece='<UNK>',
        max_sentencepiece_length=max_word_count
    )
    

def word_tokenized_sentences(input_file:str,
                             output_file:str,
                             lower_case:bool=True,
                             min_seq_len:int=5,
                             max_seq_len:int=300,
                             max_buffer_size:int=32) -> tuple[int, int]:

    if os.path.exists(input_file) == False:
        return 0, 0
    
    chunk_size = -1
    if max_buffer_size != None:
        chunk_size = max_buffer_size * 1024 * 1024 # in bytes

    k = 1
    sentence_count = 0
    max_word_count = 0
    with open(output_file, mode='w', encoding='utf-8') as f_tokens:
        with open(input_file, mode='r', encoding='utf-8') as f_ds:
            while True:
                lines = f_ds.readlines(chunk_size)
                if not lines:
                    break

                tmp = []
                for line in tqdm(lines, desc=f"Batch {k}"):
                    sent, word_count = clean_sentence(line.strip(), 
                                                      lower_case, 
                                                      min_seq_len=min_seq_len, 
                                                      max_seq_len=max_seq_len)
                    if sent == None:
                        continue
                    
                    # sent_dict = {
                    #     'sentence': sent,
                    #     'word_count': word_count
                    # }
                    # str_json = json.dumps(sent_dict, ensure_ascii=False).encode('utf-8')
                    # tmp.append(f"{str_json.decode()}\n")                
                    
                    tmp.append(f"{sent}\n")
                    max_word_count = max(max_word_count, word_count)
                    sentence_count += 1

                f_tokens.writelines(tmp)
                k += 1
            f_ds.close()
        f_tokens.close()
    return sentence_count, max_word_count


def clean_sentence(sentence:str, 
                   lower_case:bool=True, 
                   clear_punctuation:bool=False, 
                   word_with_hyphen:bool=False,
                   min_seq_len:int=5,
                   max_seq_len:int=300) -> tuple[str|None, int]:
    """
    """
    if sentence == '':
        return None
    
    words = []
    replaces = ['.', ',', '!', '?', '-', '%', ':', '/']
    punctuation = string.punctuation
    for r in replaces:
        punctuation = punctuation.replace(r, '')
    
    punctuation = list(punctuation)
    punctuation.extend(['...', '..', '....'])

    if lower_case == True:
        sentence = sentence.lower()
    
    if clear_punctuation == True:
        for r in punctuation:
            sentence = sentence.replace(r, '')

    words = word_tokenize(sentence)

    if word_with_hyphen == True:
        word_count = len(words)
        if word_count < min_seq_len or word_count > max_seq_len:
            return None, 0
        return word_tokenize(sentence, format='text'), word_count
    
    raw_text = " ".join(words)
    word_count = raw_text.count(" ") + 1
    if word_count < min_seq_len or word_count > max_seq_len:
        return None, 0
    return raw_text, word_count


if __name__ == "__main__":
    
    model_type = 'word' # unigram, bpe, word or char
    num_sent = 101000
    input_file = f"dataset/fin_all_small_{num_sent}_sentences.txt"
    output_file = f"corpus/sp_fin_all_small_space_{model_type}_tokenized_{num_sent}_sentences.txt"

    sentence_count, max_word_count = word_tokenized_sentences(input_file, 
                                                              output_file, 
                                                              min_seq_len=10, 
                                                              max_seq_len=300-1,
                                                              max_buffer_size=48)
    print(sentence_count, max_word_count)

    # max_word_count = 259
    max_word_count = min(300-1, max_word_count)
    vocab_size = 24419 # 24513
    train_sp_model(output_file,
                   model_prefix=f"corpus/sp_tokenizer_{num_sent}_sentences_model_space",
                   max_word_count=max_word_count,
                   model_type=model_type, 
                   vocab_size=vocab_size)

    
    
    # #Test encode and decode
    # txt = "đồng_thời , dự_án xây_dựng cầu_vượt nút giao lê_văn_việt , nút giao gò_công ."
    # sp = SentencePieceProcessor(model_file=f"corpus/sp_tokenizer_model_{model_type}.model")
    # # sp.load('corpus/sp_tokenizer_model_word.model')
    # encode = sp.encode_as_ids(txt)
    # print(encode)
    # print(sp.encode(txt))
    # decode = sp.decode(encode)
    # print(decode)
    # # print(decode.replace('_', ' '))
    # # print(sp.piece_to_id('<PAD>'))

    # txt = "Theo McKinsey, trong làn sóng bùng nổ GenAI còn đang tiếp diễn 3-5 năm tới, cơ hội không chỉ dành cho những người hưởng lợi đầu tiên ở tầng phần cứng dưới cùng, mà 2024 sẽ chứng kiến sự bùng nổ của tầng giữa - cơ sở hạ tầng dữ liệu, với giá trị gia tăng lớn nhất cũng như sự cạnh tranh lớn nhất nằm ở tầng ứng dụng trên cùng."
    # words = word_tokenize(txt)
    # res = " ".join(words)
    # print(res)
    # print(res.count(" "))
    # print(len(res.split(" ")))
    