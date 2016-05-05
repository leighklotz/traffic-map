#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
. ../config/config.sh

echo "$0: listing ec2 security groups"
aws ec2 describe-security-groups | gzip > ${COMPRESSED_SECURITY_GROUPS}

${DIR}/extract-by-reference.sh
