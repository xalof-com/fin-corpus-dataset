import database, model
from sqlalchemy import select, func
import pprint
from underthesea import sent_tokenize
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
    else:
        stmt = stmt.order_by(model.ArticleModel.section)
        # stmt_count = stmt_count.order_by(func.random())
    
    if n_limit != None:
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
        print(f"{count_sentences} sentences have been created.\n Saved at: {txt_file} | {zip_file}")
    else:
        print(f"{count_sentences} sentences have been created.\n Saved at: {txt_file}")
    
    return count_sentences

def extract_sentences_from_file(files:list, output_file:str, zip_it:bool=True) -> int:
    
    count_sentences = 0
    with open(output_file, mode='w', encoding='utf-8') as f_out:
        for file_name, total_rows in tqdm(files):
            with open(file_name, mode='r', encoding='utf-8') as f_in:
                k_rows = 0
                sentences = []
                for line in f_in:
                    if k_rows >= total_rows:
                        break
                    sentences.append(f"{line.strip()}\n")
                    k_rows += 1

                f_out.writelines(sentences)
                count_sentences += len(sentences)

                f_in.close()
        f_out.close()

    if zip_it == True:
        zip_file = f"{output_file}.zip"
        _create_zipfile(input_file=output_file, output_file=zip_file)

    if zip_it == True:
        print(f"{count_sentences} sentences have been created.\n Saved at: {output_file} | {zip_file}")
    else:
        print(f"{count_sentences} sentences have been created.\n Saved at: {output_file}")

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
        _clean_paragragh(article.title),
        _clean_paragragh(article.intro)
    ]
    if article.content != '':
        for p in article.content.split("\n"):
            tmp.append(_clean_paragragh(p))

    sentences = sent_tokenize(" ".join(tmp))   

    return sentences

def _clean_paragragh(txt:str) -> str:
    ending_patterns = {
        '?.': '? ',
        '!.': '! ',
        ':.': '.'
    }
    for k, v in ending_patterns.items():
        if txt.endswith(k):
            txt = txt.replace(k, v)
            break

    special_pattern = {
        '...': '. ',
        '...v.v.': '. ',
        '... v.v': '. ',
        'v.v.': '. ',
        'v.v': '. ',
        '..': '. ',
        '....': '. ',        
        '(i)': '',
        '(ii)': '',
        '(iii)': '',
        '(iv)': '',
        '(v)': '',
        '(vi)': '',
        '(vii)': '',
        '(viii)': '',
        '(ix)': '',
        '(x)': ''
    }
    for k, v in special_pattern.items():
        txt = txt.replace(k, v)

    return txt



if __name__ == "__main__":

    total = (100 * 1000) + 1000
    num_per_section = total // 4

    output_file = f"dataset/fin_all_small_{total}_sentences.txt"

    # count = create_sentences_from_articles(output_file,
    #                                     source_name=['cafef.vn'],
    #                                     max_row_buffer=2000, 
    #                                     sections=None)

    files = [
        ("dataset/fin_bat-dong-san_sentences.txt", num_per_section),
        ("dataset/fin_tai-chinh_sentences.txt", num_per_section),
        ("dataset/fin_chung-khoan_sentences.txt", num_per_section),
        ("dataset/fin_doanh-nghiep_sentences.txt", num_per_section)
    ]
    count = extract_sentences_from_file(files, output_file)
        