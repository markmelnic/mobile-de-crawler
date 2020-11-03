import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# generate the live graph
def live_graph(crawler):
    plt.style.use("dark_background")
    fig, (links_plot, perf_plot) = plt.subplots(2)
    fig.canvas.set_window_title("Crawler Activity Visualizer")

    # timestamps = []
    # try:
    #    timestamps.append(time.time() - timestamps[-1])
    # except IndexError:
    #    timestamps.append(time.time())

    # performance plot data
    crawler.interval_processed = []

    # al - active links
    # pl - processed links
    # lu - listings rewrite_table_values
    crawler.al_history = []
    crawler.pl_history = []
    crawler.lu_history = []

    def animate(i):
        # links plot
        crawler.limit_size(crawler.al_history, len(crawler.active_links))
        crawler.limit_size(crawler.pl_history, len(crawler.processed_links))
        crawler.limit_size(crawler.lu_history, len(crawler.listings_links))

        links_plot.clear()
        links_plot.plot(
            crawler.pl_history,
            crawler.al_history,
            label="Active links",
            color="#f4a261",
        )
        links_plot.plot(
            crawler.pl_history,
            crawler.lu_history,
            label="Nr. of listings",
            color="#2a9d8f",
        )
        links_plot.set_title("")
        links_plot.set_xlabel("Processed links")
        links_plot.set_ylabel("Number of urls")
        links_plot.legend()

        # performance plot
        try:
            crawler.limit_size(
                crawler.interval_processed,
                crawler.pl_history[-1] - crawler.pl_history[-2],
            )
        except IndexError:
            crawler.limit_size(crawler.interval_processed, 0)
        perf_plot.clear()
        perf_plot.plot(
            crawler.pl_history,
            crawler.interval_processed,
            label="Interval",
            color="#e9c46a",
        )
        perf_plot.set_title("Crawler performance")
        perf_plot.set_xlabel("Number of processed links")
        perf_plot.set_ylabel("Processed per iterations")
        perf_plot.legend()

    anim = animation.FuncAnimation(fig, animate, interval=1000)
    plt.show()
