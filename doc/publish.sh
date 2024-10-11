#! /bin/sh
remote='\\fauve.win.ansys.com\Int\scadeoneapi' 

# ==================================================
# Doc
usage="Usage: $0 [-h | -publish]"
if [ "x$1" = "x" ]
then
    echo $usage
    exit 0
elif [ "$1" = "-h" -o "$1" = "--help" ]
then
cat <<HELP
Publish Scade One API documentation on $remote.

$usage

HELP
exit 0
fi

# ==========================================
# Helper
# https://stackoverflow.com/questions/238073/how-to-add-a-progress-bar-to-a-shell-script
function ProgressBar {
    # Process data
    let _progress=(${1}*100/${2}*100)/100
    let _done=(${_progress}*4)/10
    let _left=40-$_done
    # Build progressbar string lengths
    _fill=$(printf "%${_done}s")
    _empty=$(printf "%${_left}s")

    printf "\rProgress : [${_fill// /#}${_empty// /.}] ${_progress}%%"
}

# Body

echo "Access to $remote takes time..."

if [ ! -d $remote ]
then
    mkdir $remote
fi

cd $(dirname $0)/_build/html
total_files=$(ls -R . | wc -l)

tar -czf - . | (
    cd $remote
    tar xzvf - 
) | (
    count=0
    partial=0
    ProgressBar $partial $total_files
    while read l
    do
        count=$[count+1]
        if [ $count -eq 10 ]
        then
            partial=$[partial+10]
            ProgressBar $partial $total_files
            count=0
        fi
    done
    ProgressBar 100 100
    echo
)

echo "Done."



