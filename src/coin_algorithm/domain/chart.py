from coin_algorithm.domain.plot import Plot


class Chart:
    def __init__(
            self, name, is_overlay=False, background_color="#FFFFFF", width=0, height=0, plot_list: [Plot] = None
    ):
        self.is_overlay = is_overlay
        self.name = name
        self.background_color = background_color
        self.width = width
        self.height = height
        self.plot_list: [Plot] = plot_list if plot_list is not None else []

    def to_proto_dict(self):
        return {
            "name": self.name,
            "isOverlay": self.is_overlay,
            "backgroundColor": self.background_color,
            "width": self.width,
            "height": self.height,
            "plotList": [plot.to_proto_dict() for plot in self.plot_list],
        }

    def add_plot(self, plot):
        self.plot_list.append(plot)
