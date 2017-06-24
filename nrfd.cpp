#include <cstdlib>
#include <iostream>
#include <sstream>
#include <string>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>

#include <glib.h>

#define ESE_UNIX_SOCKET	"ESEmbarcados"

static GMainLoop *main_loop;
static GOptionEntry options[] = {
	{ NULL }
};

static void sig_term(int sig)
{
	g_main_loop_quit(main_loop);
}

static int unix_connect(void)
{
	int sock;
	struct sockaddr saddr = {AF_UNIX, ESE_UNIX_SOCKET};
	socklen_t saddrlen = sizeof(struct sockaddr) + strlen(ESE_UNIX_SOCKET);

	sock = socket(AF_UNIX, SOCK_STREAM, 0);
	if (sock < 0)
		return -errno;

	if (connect(sock, &saddr, saddrlen) == -1) {
		close(sock);
		return -errno;
	}

	return sock;
}

static ssize_t unix_recv(int sockfd, void *buffer, size_t len)
{
	return recv(sockfd, buffer, len, 0);
}

static ssize_t unix_send(int sockfd, const void *buffer, size_t len)
{
	return send(sockfd, buffer, len, 0);
}

static void watch_io_destroy(gpointer user_data)
{
	/* TODO: Cleanup */
}

static gboolean watch_io_read(GIOChannel *io, GIOCondition cond,
							gpointer user_data)
{
	GError *gerr = NULL;
	GIOStatus status;
	char buffer[128];
	size_t rx;

	if (cond & (G_IO_ERR | G_IO_HUP | G_IO_NVAL))
		return FALSE;

	/* Reading data from audio manager */
	status = g_io_channel_read_chars(io, buffer, sizeof(buffer),
								&rx, &gerr);
	if (status != G_IO_STATUS_NORMAL) {
		printf("glib read(): %s\n", gerr->message);
		g_error_free(gerr);
		return FALSE;
	}

	printf("%s\n", buffer);

	return TRUE;
}

void manager_stop(void)
{
	/* TODO: cleanup */
	printf("%s\n", "Exiting");
}

int manager_start(void)
{
	GIOCondition cond = (GIOCondition) (G_IO_IN | G_IO_ERR 
						|  G_IO_HUP |  G_IO_NVAL);
	GIOChannel *io;
	int sock, err;

	sock = unix_connect();
	if (sock < 0) {
		printf("connect(): %s(%d)\n", strerror(-err), -err);
		return -err;
	}

	/* Watch audio manager socket */
	io = g_io_channel_unix_new(sock);
	g_io_channel_set_flags(io, G_IO_FLAG_NONBLOCK, NULL);
	g_io_channel_set_close_on_unref(io, TRUE);
	g_io_channel_set_encoding(io, NULL, NULL);
	g_io_channel_set_buffered(io, FALSE);

	g_io_add_watch_full(io, G_PRIORITY_DEFAULT, cond, watch_io_read,
							NULL, watch_io_destroy);
	g_io_channel_unref(io);

	/* TODO: Init radio */

	return 0;
}

int main(int argc, char *argv[])
{
	GOptionContext *context;
	GError *gerr = NULL;
	int err;
	guint watch_id;

	context = g_option_context_new(NULL);
	g_option_context_add_main_entries(context, options, NULL);

	if (!g_option_context_parse(context, &argc, &argv, &gerr)) {
		g_printerr("Invalid arguments: %s\n", gerr->message);
		g_error_free(gerr);
		g_option_context_free(context);
		return EXIT_FAILURE;
	}
	g_option_context_free(context);

	printf("%s\n","Daemon started");
	main_loop = g_main_loop_new(NULL, FALSE);

	err = manager_start();
	if (err < 0) {
		printf("start(): %s (%d)\n", strerror(-err), -err);
		g_main_loop_unref(main_loop);
		goto failure;
	}

	signal(SIGTERM, sig_term);
	signal(SIGINT, sig_term);
	signal(SIGPIPE, SIG_IGN);

	g_main_loop_run(main_loop);

	g_main_loop_unref(main_loop);

	g_source_remove(watch_id);

	manager_stop();

	printf("%s\n", "Exiting main");

	return EXIT_SUCCESS;

failure:
	return EXIT_FAILURE;
}
