'''
Name;Url;ReferenceDate;Developer;IsTopDeveloper;DeveloperURL;DeveloperNormalizedDomain;Category;IsFree;Price;Reviewers;Score.Total;Score.Count;Score.FiveStars;Score.FourStars;Score.ThreeStars;Score.TwoStars;Score.OneStars;Instalations;CurrentVersion;AppSize;MinimumOSVersion;ContentRating;HaveInAppPurchases;DeveloperEmail;DeveloperWebsite;PhysicalAddress;LastUpdateDate;CoverImgUrl
'''
import codecs
import re

from tqdm import tqdm

with codecs.open('../data/PlayStore_Full_2016_01_NoDescription_CSV.csv', "r", 'utf-8') as f:
    datainput = [x.strip() for x in tqdm(f)]

name_cat = []
possible_cat = set()
for i in datainput:
    try:
        iarr = i.split(';')
        name = re.findall('id=(.+)', iarr[1])
        name_cat.append((name[0], iarr[7]))
        # possible_cat.add(iarr[7])
    except:
        print(i)

with open('../data/category.txt', 'w') as f:
    for i in name_cat:
        f.write('{}\t{}\n'.format(i[0], i[1]))

# print(possible_cat)
