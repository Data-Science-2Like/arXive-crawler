import os
import tarfile
from tqdm import tqdm
from database import getYearOfPaper




def count_ocurrences(source):
    # we need to set the enviroment variable here for the perl script to use this as
    # a working directory
    bib_count = 0
    total_count = 0

    total_counts = dict()
    bib_counts = dict()

    for filename in tqdm(os.listdir(source)):
        if filename.endswith("tar.gz"):
            idStr = filename.split(".")[0]

            has_bib = False
            try:
                tar = tarfile.open(os.path.join(source, filename))
                file = tar.next()
                while file != None:
                    if file.name.endswith(".bib"):
                        has_bib = True
                        break
                    file = tar.next()
            except Exception:
                continue

            year = getYearOfPaper(idStr)
            if has_bib:
                bib_count += 1
                if year in bib_counts:
                    bib_counts[year] += 1
                else:
                    bib_counts[year] = 1
            if year in total_counts:
                total_counts[year] += 1
            else:
                total_counts[year] = 1
            total_count += 1

    print("Total Count: ", total_count)
    print(f"Bib Count: {bib_count} ({bib_count / total_count})")

    print("--- YEARS ----")
    for year in total_counts.keys():
        if year in bib_counts:
            print(f"{year}: Total Count: {total_counts[year]} Bib Count: {bib_counts[year]} ({bib_counts[year] / total_counts[year]})")
        else:
            print(f"{year}: ----")


