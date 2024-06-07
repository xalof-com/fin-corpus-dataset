import database, model
from sqlalchemy import select, func
import pprint
from underthesea import word_tokenize, sent_tokenize
import os, string, json
from tqdm import tqdm
import zipfile
from zipfile import ZipFile


def create_sentences_from_articles(
        output_file:str, 
        source_name:list=None, 
        sections:list=None, 
        n_limit:int=None, 
        max_row_buffer:int=1000,
        zip_it:bool=True) -> int:
    """
    """
    
    stmt = select(model.ArticleModel)
    stmt_count = select(func.count(model.ArticleModel.id))
    if source_name != None:
        stmt = stmt.where(model.ArticleModel.source_name.in_(source_name))
        stmt_count = stmt_count.where(model.ArticleModel.source_name.in_(source_name))
    if sections != None:
        stmt = stmt.where(model.ArticleModel.section.in_(sections))
        stmt_count = stmt_count.where(model.ArticleModel.section.in_(sections))
    if n_limit != None:
        stmt = stmt.order_by(func.random())
        stmt_count = stmt_count.order_by(func.random())
        stmt = stmt.limit(n_limit)
        stmt_count = stmt_count.limit(n_limit)
   
    if isinstance(sections, list) and len(sections) == 1:
        txt_file = output_file.format(sections[0])
    else:
        txt_file = output_file.format('all')

    if os.path.dirname(output_file) != '':
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print('Starting...')
    count_sentences = 0
    with open(txt_file, mode='w', encoding='utf-8') as f:
        with database.DbSession() as session:
            total = session.execute(stmt_count).scalar()
            batches = total // max_row_buffer
            if total % max_row_buffer != 0:
                batches += 1
            print(f"Total batches: {batches}. {max_row_buffer} rows/batch")
            stmt = stmt.execution_options(yield_per=max_row_buffer)
            # for partition in session.scalars(stmt).partitions():
            for partition in tqdm(session.scalars(stmt).partitions(), total=batches):
                for article in partition:   
                    sentences = _create_sentences(article)
                    count_sentences += len(sentences)
                    payload = "\n".join(sentences)
                    f.write(f"{payload}\n")
        f.close()
    
    if zip_it == True:
        if isinstance(sections, list) and len(sections) == 1:
            zip_file = output_file.format(f"{sections[0]}_{count_sentences}")
        else:
            zip_file = output_file.format(f"all_{count_sentences}")
        zip_file = f"{zip_file}.zip"
        _create_zipfile(input_file=txt_file, output_file=zip_file)

    print('Finished!')

    if zip_it == True:
        print(f"{count_sentences} sentences have been created. Stored at: {txt_file} | {zip_file}")
    else:
        print(f"{count_sentences} sentences have been created. Stored at: {txt_file}")
    
    return count_sentences

def _create_zipfile(input_file:str, output_file:str) -> bool:
    if os.path.exists(input_file) == False:
        print(f"{input_file} cannot be found!")
        return False
    
    print("Create zip file:...")
    with ZipFile(output_file, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(input_file, os.path.basename(input_file))
        zf.close()
    
    print(f"{output_file} is created")
    return True    


def _create_sentences(article:model.ArticleModel) -> list:
    sentences = []
   
    tmp = [
        _replace_ending_paragragh(article.title),
        _replace_ending_paragragh(article.intro)
    ]
    if article.content != '':
        for p in article.content.split("\n"):
            tmp.append(_replace_ending_paragragh(p))

    sentences = sent_tokenize(" ".join(tmp))   

    return sentences

def _replace_ending_paragragh(txt:str) -> str:
    patterns = {
        '?.': '?',
        '!.': '!',
        '...': '.',
        '....': '.'
    }

    for k, v in patterns.items():
        if txt.endswith(k):
            txt = txt.replace(k, v)
            break
    return txt



if __name__ == "__main__":
    output_file = "dataset/fin_{0}_sentences.txt"
    count = create_sentences_from_articles(output_file,
                                           source_name=['cafef.vn'],
                                           max_row_buffer=2000, 
                                           sections=['doanh-nghiep'])
    