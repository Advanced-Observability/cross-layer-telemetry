// Module to enable or disable CLT in the kernel by using generic netlink

package clt_genl

import (
	"errors"
	"fmt"
	"log"
	"os"

	"github.com/mdlayher/genetlink"
	"github.com/mdlayher/netlink"
	"github.com/mdlayher/netlink/nlenc"
)

// Family name
const IOAM6_GENL_NAME string = "IOAM6"

// Attributes
const IOAM6_ATTR_SOCKFD uint16 = 8
const IOAM6_ATTR_ID_HIGH uint16 = 9
const IOAM6_ATTR_ID_LOW uint16 = 10
const IOAM6_ATTR_SUBID uint16 = 11

// Commands
const IOAM6_CMD_PKT_ID_ENABLE uint8 = 8
const IOAM6_CMD_PKT_ID_DISABLE uint8 = 9

/*
Create socket for IOAM6 generic netlink and get the IOAM6 generic netlink family.

Return:
- Created connection if no error. Else, nil.
- IOAM6 generic netlink family if no error. Else, empty family.
- Error if any. Else, nil.
*/
func ioam6_generic_netlink() (*genetlink.Conn, genetlink.Family, error) {
	// Create generic netlink socket to interact with kernel
	c, err := genetlink.Dial(nil)
	if err != nil {
		log.Printf("failed to dial generic netlink: %v\n", err)
		return nil, genetlink.Family{}, err
	}

	// Get family because depending on kernel the id for the family can change
	family, err := c.GetFamily(IOAM6_GENL_NAME)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			log.Printf("%q family not available", IOAM6_GENL_NAME)
			return nil, genetlink.Family{}, err
		}

		log.Fatalf("failed to query for family: %v", err)
	}

	return c, family, nil
}

/*
Enable CLT on the given socket for the given trace and span ids.

Parameters:
- socketFD: socket on which to enable clt
- traceIDHigh: MSB of trace id
- traceIDLow: LSB of trace id
- spanID: span id

Return:
Error if any. Else, nil.
*/
func clt_enable(socketFD uint32, traceIDHigh uint64, traceIDLow uint64, spanID uint64) error {
	c, family, err := ioam6_generic_netlink()
	if err != nil {
		fmt.Println("Error while establishing generic netlink socket")
		return err
	}
	defer c.Close()

	// Create attributes for the request
	b, err := netlink.MarshalAttributes([]netlink.Attribute{
		{
			Type: IOAM6_ATTR_SOCKFD,
			Data: nlenc.Uint32Bytes(socketFD),
		},
		{
			Type: IOAM6_ATTR_ID_HIGH,
			Data: nlenc.Uint64Bytes(traceIDHigh),
		},
		{
			Type: IOAM6_ATTR_ID_LOW,
			Data: nlenc.Uint64Bytes(traceIDLow),
		},
		{
			Type: IOAM6_ATTR_SUBID,
			Data: nlenc.Uint64Bytes(spanID),
		},
	})
	if err != nil {
		fmt.Println("Cannot create attributes for generic netlink message")
		return err
	}

	// Create message with headers + attributes
	req := genetlink.Message{
		Header: genetlink.Header{
			Command: IOAM6_CMD_PKT_ID_ENABLE,
			Version: uint8(family.Version),
		},
		Data: b,
	}

	// Send message
	flags := netlink.Request | netlink.Acknowledge
	if _, err = c.Execute(req, family.ID, flags); err != nil {
		fmt.Println("clt_enable execute error: " + err.Error())
		return err
	}

	return nil
}

/*
Disable CLT on the given socket.

Parameters:
- socketFD: socket on which to disable clt

Return:
Error if any. Else, nil.
*/
func clt_disable(socketFD uint32) error {
	c, family, err := ioam6_generic_netlink()
	if err != nil {
		fmt.Println("Error while establishing generic netlink socket")
		return err
	}
	defer c.Close()

	// Create attributes for the request
	b, err := netlink.MarshalAttributes([]netlink.Attribute{
		{
			Type: IOAM6_ATTR_SOCKFD,
			Data: nlenc.Uint32Bytes(socketFD),
		},
	})
	if err != nil {
		fmt.Println("Cannot create attributes for generic netlink message")
		return err
	}

	// Create message with headers + attributes
	req := genetlink.Message{
		Header: genetlink.Header{
			Command: IOAM6_CMD_PKT_ID_DISABLE,
			Version: uint8(family.Version),
		},
		Data: b,
	}

	// Send message
	flags := netlink.Request | netlink.Acknowledge
	if _, err = c.Execute(req, family.ID, flags); err != nil {
		fmt.Println("clt_disable execute error: " + err.Error())
		return err
	}

	return nil
}
