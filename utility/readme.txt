Make sure to correctly specify paths in each of the utility scripts.


About the script:
1. genll-par.sh: generating ll files for the files present in the submissions folder in originally created scraped folders AND creating submissions_ll sub-sub-dir in each sub-dir.

2. genVectors.sh: generating IR2Vec vectors for each of the ll files in the submissions_ll sub-dir in the main dir containing the data created using above script. Creates a new 'vectors' sub-sub-dir in each sub-dir, containing the text files.

3. getStat.sh: displays the stats about number of files and dirs in the originally created scraped data (not containing submissions_ll sub-sub-dir).

4. getStatll.sh: same function as above script but here submissions_ll folder is present.

5. clean_lldir.sh: remuoves the submissions_ll folder created in each sub-dir. Mainly used in testing the script.w

6. filterData.sh: filters the data for empty submissions and submissions_ll folders and creates a dataset that can be used to generate ir2vec vectors.
