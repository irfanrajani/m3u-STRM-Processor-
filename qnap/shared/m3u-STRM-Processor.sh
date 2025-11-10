#!/bin/sh
set -e

CONF=/etc/config/qpkg.conf
QPKG_NAME="m3u-STRM-Processor"
QPKG_ROOT=`/sbin/getcfg $QPKG_NAME Install_Path -f ${CONF}`
APACHE_ROOT=`/sbin/getcfg SHARE_DEF defWeb -d QWEB -f /etc/config/def_share.info`
export QNAP_QPKG=$QPKG_NAME

# Navigate to the package root directory
cd "$QPKG_ROOT"

# Function to log messages
log_msg() {
    echo "$(date): $1" >> "$QPKG_ROOT/qpkg.log"
}

case "$1" in
  start)
    ENABLED=$(/sbin/getcfg $QPKG_NAME Enable -u -d FALSE -f $CONF)
    if [ "$ENABLED" != "TRUE" ]; then
        log_msg "Service is disabled. Aborting start."
        exit 1
    fi

    log_msg "Starting m3u-STRM-Processor service..."
    # Use docker-compose for compatibility
    /usr/bin/docker-compose -f "$QPKG_ROOT/docker-compose.yml" up -d
    log_msg "Service started."
    ;;

  stop)
    log_msg "Stopping m3u-STRM-Processor service..."
    if [ -f "$QPKG_ROOT/docker-compose.yml" ]; then
        /usr/bin/docker-compose -f "$QPKG_ROOT/docker-compose.yml" down
    fi
    log_msg "Service stopped."
    ;;

  restart)
    log_msg "Restarting service..."
    "$0" stop
    sleep 2
    "$0" start
    log_msg "Service restarted."
    ;;

  *)
    echo "Usage: $0 {start|stop|restart}"
    exit 1
esac

exit 0