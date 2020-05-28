#include <stdlib.h>
#include <stdio.h>
#include <linux/ioam.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <unistd.h>

int main()
{
	int ret, fd;

	// =============== Data structure ================
	struct ioam_node node =
	{
		.ioam_node_id = 3,

		.if_nb = 1,
		.ifs =
		{
			{
				.ioam_if_id = 31,
				.if_name = "eth0",
				.ioam_if_mode = IOAM_IF_MODE_INGRESS
			}
		},

		.ns_nb = 1,
		.nss =
		{
			{
				.ns_id = 123,
				.ns_decap = true
			}
		}
	};
	// ===============================================

	fd = open("/dev/ioam", O_RDWR);
	if (fd == -1)
	{
		printf("Unable to open the ioam device\n");
		return 1;
	}

	ret = ioctl(fd, IOAM_IOC_REGISTER, &node);
	if (ret == IOAM_RET_OK)
		printf("OK\n");
	else
		printf("ERROR (%d)\n", ret);

	close(fd);
	return 0;
}

