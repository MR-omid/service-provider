
function status() {
	local r=$(pgrep -f 'receive')
	echo $r
}

result=$(status)
echo $result