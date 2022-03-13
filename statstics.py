import os
import tarfile
import tqdm





def count_ocurrences(source):
    # we need to set the enviroment variable here for the perl script to use this as
    # a working directory
    bib_count = 0
    total_count = 0

    for filename in os.listdir(source):
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
            if total_count % 1000 == 0:
                print('.',end = '')

            if has_bib:
                bib_count += 1
            total_count += 1

    print("Total Count: ", total_count)
    print(f"Bib Count: {bib_count} ({bib_count / total_count})")
