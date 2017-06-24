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

static GMainLoop *main_loop;
static GOptionEntry options[] = {
	{ NULL }
};

static void sig_term(int sig)
{
	g_main_loop_quit(main_loop);
}

void manager_stop(void)
{
	/* TODO: cleanup */
	printf("%s\n", "Exiting");
}

int manager_start(void)
{
	printf("%s\n", "Starting manager");

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
