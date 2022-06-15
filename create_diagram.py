import matplotlib.pyplot as plt
from database import getPaperCountsPerYearByCateogry, getPaperWithYears
import json
from collections import Counter

if __name__ == "__main__":
    fig = plt.figure()
    #ax = fig.add_axes([0, 0, 1, 1])
    data = getPaperCountsPerYearByCateogry([10, 62, 122])

    full_data = getPaperWithYears()

    valid_ids = json.load(open('valid_ids.json','r'))

    valid_data = [p for p in full_data if str(p[0]) in valid_ids] # takes some minutes
    years_v = [int(p[1]) for p in valid_data]

    texC = Counter(years_v)


    papers, years = zip(*data)

    years = [int(y) for y in years]

    tex_counts = []
    remaining_c = [
    ]
    for i,year in enumerate(years):
        if year in texC.keys():
            tex_counts.append(texC[year])
            remaining_c.append(papers[i] - texC[i])
        else:
            tex_counts.append(0)
            remaining_c.append(papers[i])

    #train_years = years[:-2]
    #train_papers = papers[:-2]

    #test_years = years[-2:]
    #test_papers = papers[-2:]

    plt.bar(years,tex_counts,label='with .bib', color='tab:green')
    plt.bar(years,remaining_c, bottom=tex_counts, label='Papers', color='tab:blue')
    plt.ylabel('Number of Papers')
    plt.xlabel('Published Year')
    plt.title('Papers per year in crawler arXiv dataset')
    plt.legend()
    #plt.show()
    plt.savefig('arXiv-year-distribution.png')