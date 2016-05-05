#!/bin/bash

screen -S traffic-mapper -d -m sh -c "./doit.sh '7:00AM tomorrow'"
screen -S visualization -d -m sh -c "cd serve; ./serve-node.sh"

echo "Now run"
echo "  screen -r traffic-mapper"
echo "give password, and exit screen with Ctrl-A d"
echo ""
echo "use utils/howlong and utils/howfar to monitor progress"

