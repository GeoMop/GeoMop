import .analysis


def test_repr_workflow():
    @workflow
    def


# """ Possibly we can provide a tools how to write own actions and composed workflows in a Python way.
# we jst need a types that allow any kind of operation and behave like a type that have desired structure. All used actions should
# handle empty type trees, not sure about all python functions."""
# @workflow
# def extract_abs_velocity_observations(observe_yaml, measure_times):
#     """
#     Example how to make an action (with build in converter) as a python code.
#     :param observe_yaml: Parsed observe output from flow
#     :param measure_times: List of times in which the velocity has been measured.
#
#     The same code can posibly be used to implement an action we just have to use an @function_action decorator, that
#     compose appropriate class whith input and output types obtained in the same way as in the case of @workflow decorator.
#     """
#     observe_data = observe_yaml.data
#     all_velocities = [ (time_frame.time, time_frame.velocity) for time_frame in observe_data]
#     measure_times_velocities = ac.interpolate(all_velocities, measure_times, type='linear')
#     return [ ac.norm(vel) for vel in measure_times_velocities]
#
# w = Workflow()
# w.
