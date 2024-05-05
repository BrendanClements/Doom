import CME
import PowerGrid

"""

"""
#  TODO: Create alert methods utilizing sound, lights, and digital communication to convey messages.
#  TODO: Program logic to determine severity of returned indicators and trigger alert based on results.
#  TODO: Prevent false positives by utilizing backup methods to recheck indicators where possible.
#  TODO: Check local indicators i.e. is there power to the outlet, internet access, cell signal, active radio stations?
#  TODO: Make method for returning we requests and incorporate that into PowerGrid and CME.
#  TODO: Add time checks to get ETA for completion of longer operations.


def collector():
    """
    Retrieves the result from every method that queries indicators for
    a local or national emergency.
    """
    func = {'CME': CME.cme(),
            'PowerGrid': PowerGrid.grid_outages()}
    return func


def logic():
    """
    Retrieves the result from every method that queries indicators for
    a local or national emergency, determines how emergent the threat is
    and triggers an alert based on those factors.
    """
    indicators = collector()


if __name__ == "__main__":
    print("Hello, World!")
