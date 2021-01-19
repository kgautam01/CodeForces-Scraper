# Script for filtering the main directory containing scraped data and respective ll files and creating new dir containing this filtered data with no empty submissions, submissions_ll folder in it. This dir is consumed by genVectors.sh script to generate respective IR2Vec vectors.

Dir="/home/cs20mtech01004/cofoscraper/cpp17Data"
for dir in $Dir/*;do
	if [ -d $dir/submissions_ll ];then
		echo "$dir/submissions_ll"
		cp -r $dir ./dataCpp17
	fi
done
