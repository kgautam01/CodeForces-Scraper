# This is a parallel version of a script to generate ll files for the 'submissions' folder containing atleast a file (an if check is maintained).
# Requirements:
# Install GNU parallel using apt before using this script and specify the number of threads as per the need and H/W specifications.
# DIR defines the main directory containing sub-dirs in which submissions folder is present.

DIR="/home/cs20mtech01004/cofoscraper/test"
for dir in $DIR/*;do
	if [ -d $dir ];then	
		if [ "$(ls -A $dir/submissions)" ];then	
			mkdir $dir/submissions_ll
			cd $dir/submissions
			# Change *.cpp to *.c for generating ll files for c program files.
			parallel -j10 clang++-10 -std=c++17 -w -S -emit-llvm {} -o ../submissions_ll/{.}.ll ::: *.cpp
			echo "-------------------------"
			echo "Number of c/cpp files in $dir: `ls | wc -l`"
			echo "Number of generated ll files in $dir: `ls ../submissions_ll | wc -l`"
			echo "-------------------------"
			cd ../../
		fi
	fi
done
