dirCounter=0
totalDir=0
totalFilesCounter=0
dpgte500=0
dp200to300=0
dp300to500=0
dp100to200=0
for dir in $1/*;do
        let "totalDir+=1"
        if [ -d $dir ]; then
                filesCounter=0
                if [ -n "$(ls $dir/submissions)" ]; then
                        let "dirCounter+=1"
                        let "filesCounter = "$(ls $dir/submissions | wc -l)""
#                       echo "filesCounter: $filesCounter"

                        if (( $filesCounter >= 500 ));then
                                let "dpgte500+=1"
                                echo "Files in $dir/submissions: $filesCounter"
                        fi
                        if (( $filesCounter >= 200 && $filesCounter <= 300 ));then
                                let "dp200to300+=1"
                                echo "Files in $dir/submissions: $filesCounter"
                        fi
                        if (( $filesCounter > 300 && $filesCounter < 500 ));then
                                let "dp300to500+=1"
                                echo "Files in $dir/submissions: $filesCounter"
                        fi
                        if (( $filesCounter >= 100 && $filesCounter < 200 ));then
                                let "dp100to200+=1"
                                echo "Files in $dir/submissions: $filesCounter"
                        fi
                        let "totalFilesCounter+=$filesCounter"
                fi
        fi
done
echo "Total number of dir: $totalDir"
echo "Total number of non-empty dir: $dirCounter"
echo "Total number of source code files: $totalFilesCounter"
echo "Classes with Data points in range [100, 200): $dp100to200"
echo "Classes with Data points in range [200,300]: $dp200to300"
echo "Classes with Data points in range (300, 500): $dp300to500"
echo "Classes with Data points >= 500: $dpgte500"

