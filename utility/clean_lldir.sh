DIR="/home/cs20mtech01004/cofoscraper/cpp17Data"
for dir in $DIR/*;do
	if [ -d $dir ];then
		rm -r $dir/submissions_ll
	fi
done
