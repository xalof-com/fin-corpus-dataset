from underthesea import word_tokenize
import os, string, json
# import zipfile
# from zipfile import ZipFile
from tqdm import tqdm
from typing import Iterable, Any


def get_stopwords(input_file:str) -> list:
    """
    Load the stopwords list from file.
    
    Parameters:
        input_file: stopwords file's path.

    Return:
        stopwords: list of stopwords.

    """
    if os.path.exists(input_file) == False:
        return []
    
    stopwords = []
    with open(input_file, 'r', encoding='utf-8') as f:
        stopwords = [line.strip() for line in f]
    return stopwords

def _sentence_to_words(sentence:str, lower_case:bool=True, list_stopwords:list=None) -> list:
    """
    Separate the sentence into words apart.

    Parameters:
        sentence: target sentence to be separated.
        list_stopwords: list of stopwords.

    Return:
        words: the list of words apart.
    """
    words = []
    replaces = ['.', ',', '!', '?', '-', '%', ':', '/']
    punctuation = string.punctuation
    for r in replaces:
        punctuation = punctuation.replace(r, '')
    
    punctuation = list(punctuation)
    punctuation.extend(['...', '..', '....'])

    if lower_case == True:
        sentence = sentence.lower()
    
    if list_stopwords == None or (isinstance(list_stopwords, list) and len(list_stopwords) == 0):
        for r in punctuation:
            sentence = sentence.replace(r, '')
        words = word_tokenize(sentence)
        
    else:
        for r in punctuation:
            sentence = sentence.replace(r, '')

        for word in word_tokenize(sentence):
            if word not in list_stopwords:
                words.append(word)

    return words

def create_word_tokenized_sentences(input_file:str, output_file:str, list_stopwords:list=None, min_seq_len:int=5, max_buffer_size:int=32) -> int:
    """
    Create the sentence from raw text to list of word tokenized and word_count. Then save them to file.

    Parameters:
        input_file: is the file of raw text (each sentence per line)
        output_file: out put file name
        list_stopwords: list of stop words
        max_buffer_size: the max number of MB for buffering the lines per batch

    Return:
        sentence_count: total sentences has been converted to word tokenized
    """
    if os.path.exists(input_file) == False:
        return 0

    size_hint = -1
    if max_buffer_size != None:
        size_hint = max_buffer_size * 1024 * 1024 # in bytes

    k = 1
    sentence_count = 0
    with open(output_file, mode='w', encoding='utf-8') as f_tokens:
        with open(input_file, mode='r', encoding='utf-8') as f_ds:
            while True:
                lines = f_ds.readlines(size_hint)
                if not lines:
                    break
                
                tmp = []
                for line in tqdm(lines, desc=f"Batch {k}"):
                    if line.strip() == '':
                        continue

                    word_tokens = _sentence_to_words(line.strip(), lower_case=True, list_stopwords=list_stopwords)
                    word_count = len(word_tokens)
                    if (word_count - 1) > min_seq_len:
                        sent_dict = {
                            'sentence': word_tokens,
                            'word_count': word_count
                        }
                        str_json = json.dumps(sent_dict, ensure_ascii=False).encode('utf-8')
                        tmp.append(f"{str_json.decode()}\n")                
                        sentence_count += 1
                
                f_tokens.writelines(tmp)
                k += 1
            f_ds.close()
        f_tokens.close()
    return sentence_count

def create_unique_word_tokens(input_file:str, max_buffer_size:int=32) -> tuple[set, int]:
    """
    Load word tokenized from file and produce the unique word list.

    Parameters:
        input_file: word tokenized sentences file.
        max_buffer_size: the buffer size can read per batch.

    Return:
        tokens: the unique list of word tokens
        max_seq_len: the max sequence len
    """
    if os.path.exists(input_file) == False:
        print(f"Cannot find this file: {input_file}")
        return None, 0
    
    size_hint = -1
    if max_buffer_size != None:
        size_hint = max_buffer_size * 1024 * 1024

    # sentences = []
    k = 1
    tokens = set()
    max_seq_len = 0
    with open(input_file, mode='r', encoding='utf-8') as f:
        while True:
            lines = f.readlines(size_hint)
            if not lines:
                break

            for line in tqdm(lines, desc=f"Batch {k}"):
                if line.strip() == '':
                    continue
                sent_dict = json.loads(line.strip())
                max_seq_len = max(max_seq_len, sent_dict['word_count'])
                tokens.update(sent_dict['sentence'])
            k += 1
        f.close()
    return tokens, max_seq_len

def create_vocab_with_index(word_tokens:Iterable, special_tokens:list=None, vocab_file:str=None, forced:bool=False) -> dict:
    """
    Create the vocab json file.

    Parameters:
        word_tokens: the list of unique word tokens
        special_tokens: if None: the default are: <SOS>, <EOS>, <PAD>, <UNK>
        vocab_file: vacab file output
        forced: if True: Load and create new vocab file

    Return:
        vocab
    """
    if forced == False and vocab_file != None and os.path.exists(vocab_file):
        with open(vocab_file, mode='r', encoding='utf-8') as f:
            vocab = json.loads(f.read().strip())
            f.close()
            print(f"Load vocab from file: {vocab_file}")
        return vocab

    tokens = {}
    start_idx = 0
    if special_tokens == None:
        tokens = {
            "<SOS>": 0,
            "<EOS>": 1,
            "<PAD>": 2,
            "<UNK>": 3
        }
        start_idx = 4
    else:
        for i, token in enumerate(special_tokens):
            tokens[token] = i
        start_idx = len(special_tokens)
        
    for i, token in enumerate(tqdm(word_tokens, desc="Vocab"), start_idx):
        tokens[token] = i
    
    vocab = {
        'size': len(tokens),
        'tokens': tokens
    }
        
    with open(vocab_file, mode='w', encoding='utf-8') as f:
        str_json = json.dumps(vocab, indent=2, ensure_ascii=False).encode('utf-8')
        f.write(str_json.decode())
        f.close()
    return vocab


if __name__ == "__main__":
    corpus_dir = 'corpus'
    dataset_dir = 'dataset'
    stopwords_dir = "stopwords"

    section = 'all_small'
    dataset_file = f"{dataset_dir}/fin_{section}_sentences.txt"
    word_tokenized_file = f"{corpus_dir}/fin_{section}_word_tokenized_sentences.txt"
    stopwords_file = f"{stopwords_dir}/vietnamese-stopwords.txt"

    vocab_file = f"{corpus_dir}/fin_{section}_vocab.json"

    # list_stopwords = get_stopwords(stopwords_file)
    # sent_count = create_word_tokenized_sentences(dataset_file, word_tokenized_file, max_buffer_size=32)
    # print(f"Sentence: {sent_count}")

    print(f"\nCreate vocab from file: {word_tokenized_file}")
    word_tokens, max_seq_len = create_unique_word_tokens(word_tokenized_file, max_buffer_size=32)
    vocab = create_vocab_with_index(word_tokens, vocab_file=vocab_file, forced=True)
    print(f"Vocab size: {vocab['size']}")