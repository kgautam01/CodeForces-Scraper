# Parallelized script for generating IR2Vec vectors for the ll files present in the submissions_ll folder of each sub-dir in dataDir.
# Make sure to increase the stack space to unlimited before running this script using 'ulimit -s unlimited'

dataDir="/home/cs20mtech01004/cofoscraper/dataCpp17"

# Requirements:
# 1. GNU 'parallel' (available on apt).
# 2. IR2Vec binary and seed embedding vocab txt file (for v10.0.1 of llvm)
# 3. Opt-V10.0.1 (can be installe using apt)

for dir in $dataDir/*;do
        if [ -d $dir ];then
                if [ -d $dir/submissions_ll ];then
                        cd $dir/submissions_ll
#                       Don't mention absolute path for the output.txt file.
                        parallel -j8 opt-10 -load ~/cofoscraper/libIR2Vec-RD.so -IR2Vec_RD -file ~/cofoscraper/seedEmbeddingVocab-300-llvm10.txt -of {.}.txt -level p {} --bpi 0 -o /dev/null ::: *.ll
                        echo "-------------------------"
                        echo "Number of c/cpp files in $dir: `ls ../submissions | wc -l`"
                        echo "Number of generated ll files in $dir: `ls *.ll | wc -l`"
			rm cyclicCount_*.txt && rm missCount_*.txt
                        mkdir $dir/vectors
                        mv *.txt ../vectors
			echo "Number of txt files generated in $dir: `ls ../vectors | wc -l`"
			echo "-------------------------"
                        cd ../../
                fi
        fi
done

