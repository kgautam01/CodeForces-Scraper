# Script for collecting the stats on dir(dataCpp17), created after generation of ll files, passed as arguments and is present in the cwd.

dirCounter=0
totalDir=0
totalFilesCounter=0
for dir in ./$1/*;do
        let "totalDir+=1"
        if [ -d $dir ]; then
                filesCounter=0
                if [ -d $dir/submissions_ll ]; then
                        let "dirCounter+=1"
                        let "filesCounter = "$(ls $dir/submissions_ll | wc -l)""
#                       echo "filesCounter: $filesCounter"
                        echo "Files in $dir/submissions_ll: $filesCounter"
                        let "totalFilesCounter+=$filesCounter"
#                       echo "totalFilesCounter: $totalFilesCounter"
        #       else
        #               echo "$dir/submissions is Not Empty"
                fi
        fi
done
echo "Total number of dir: $totalDir"
echo "Total number of non-empty dir: $dirCounter"
echo "Total number of ll files: $totalFilesCounter"
