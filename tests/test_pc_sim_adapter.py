from core.hardware.pc_sim_adapter import PcSimAdapter


def test_pc_sim_adapter_register_and_read():
    adapter = PcSimAdapter()
    adapter.register_sensor("temp", initial_value=25.0, unit="C")
    adapter.register_actuator("fan", initial_value=0.0)

    reading = adapter.read_sensor("temp")
    assert reading.value == 25.0
    assert reading.unit == "C"

    value = adapter.write_actuator("fan", 1.0)
    assert value == 1.0
    assert adapter.actuators["fan"] == 1.0
