# Unit Tests for the PyDMSlider Widget

import pytest
from logging import ERROR
import numpy as np

from qtpy.QtWidgets import QLabel, QSlider, QVBoxLayout, QHBoxLayout, QSizePolicy
from qtpy.QtCore import Qt, Property, QMargins

from pydm.widgets.slider import PyDMSlider
from pydm.widgets.base import PyDMWidget


# --------------------
# POSITIVE TEST CASES
# --------------------

def test_construct(qtbot):
    """
    Test the construction of the widget.

    Expectations:
    Default values are correctly assigned.

    Parameters
    ----------
    qtbot : fixture
        Window for widget testing
    """
    pydm_slider = PyDMSlider()
    qtbot.addWidget(pydm_slider)

    assert pydm_slider.alarmSensitiveContent is True
    assert pydm_slider.alarmSensitiveBorder is False
    assert pydm_slider._show_limit_labels is True
    assert pydm_slider._show_value_label is True
    assert pydm_slider._user_defined_limits is False
    assert pydm_slider._needs_limit_info is True
    assert pydm_slider._minimum is None
    assert pydm_slider._maximum is None
    assert pydm_slider._user_minimum == -10.0
    assert pydm_slider._user_maximum == 10.0
    assert pydm_slider._num_steps == 101
    assert pydm_slider.orientation == Qt.Horizontal
    assert pydm_slider.isEnabled() is False

    assert type(pydm_slider.low_lim_label) == QLabel
    assert pydm_slider.low_lim_label.sizePolicy() == QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
    assert pydm_slider.low_lim_label.alignment() == Qt.Alignment(Qt.AlignLeft | Qt.AlignTrailing | Qt.AlignVCenter)


    assert type(pydm_slider.high_lim_label) == QLabel
    assert pydm_slider.high_lim_label.sizePolicy() == QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
    assert pydm_slider.high_lim_label.alignment() == Qt.Alignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)


    assert type(pydm_slider._slider) == QSlider
    assert pydm_slider._slider.orientation() == Qt.Orientation(Qt.Horizontal)

    assert pydm_slider._slider_position_to_value_map is None
    assert pydm_slider._mute_internal_slider_changes is False
    assert pydm_slider._orientation == Qt.Horizontal


def test_init_for_designer(qtbot):
    """
    Test the configuration method for using with Qt Designer.

    Expectations:
    The widget's internal value is set to 0.0.

    Parameters
    ----------
    qtbot : fixture
        Window for widget testing
    """
    pydm_slider = PyDMSlider()
    qtbot.addWidget(pydm_slider)

    pydm_slider.init_for_designer()
    assert pydm_slider.value == 0.0


def test_actions_triggered(qtbot):
    """
    Test emitting values via the widget's action slots.

    Expectations:
    The slot's actions are triggered.

    qtbot : fixture
        pytest-qt window for widget test
    """
    pydm_slider = PyDMSlider()
    qtbot.addWidget(pydm_slider)

    pydm_slider.internal_slider_action_triggered(1)

    pydm_slider.internal_slider_pressed()

    pydm_slider.internal_slider_released()


@pytest.mark.parametrize("new_value, mute_change", [
    (100.50, False),
    (-100, True),
])
def test_internal_slider_value_changed(qtbot, new_value, mute_change):
    """
    Test widget's change of its text value if its internal value has changed.

    Expectations:
    If the `_mute_internal_slider_changes` flag is True, the value will not be propagated to PyDM, and the
    send_value_signal will not emit the new value (avoiding the infinite loop).

    Parameters
    ----------
    qtbot : fixture
        pytest-qt window for widget test
    new_value : int
        The new value from changing the slider widget.
    mute_change : bool
        True if the new slider value is not to be propagated; False otherwise.
    """
    pydm_slider = PyDMSlider()
    qtbot.addWidget(pydm_slider)

    def foo(val):
        pydm_slider.test_write = val
    pydm_slider.write_to_channel = foo
    pydm_slider.test_write = None

    pydm_slider.userDefinedLimits = True
    pydm_slider.userMinimum = 10
    pydm_slider.userMaximum = 100

    pydm_slider.value = 123
    pydm_slider._mute_internal_slider_changes = mute_change

    # If the slider emits the new value, the fixture's receiveValue should get it. This should happen if the slider's
    # internal changes are not muted, and should NOT if it IS muted
    pydm_slider.internal_slider_value_changed(new_value)

    if not mute_change:
        # The internal_slider_value_changed_slot emitted the send_value_signal
        assert pydm_slider.test_write == pydm_slider.value
    else:
        # The internal_slider_value_changed_slot did NOT emit the send_value_signal.
        assert pydm_slider.test_write is None


@pytest.mark.parametrize("show_labels, tick_position", [
    (True, 0),
    (True, -10),
    (True, 10),
    (False, 0),
    (False, -10),
    (False, 10),
])
def test_properties_and_setters(qtbot, show_labels, tick_position):
    """
    Test the widget's various properties and setters.

    Expectations:
    The setters will update the values of the corresponding properties, which will return the up-to-date values.

    Parameters
    ----------
    qtbot : fixture
        pytest-qt window for widget test
    show_labels : bool
        True if the labels (min and max values) will be shown; False otherwise
    tick_position : int
        The tick position for the slider component.
    """
    pydm_slider = PyDMSlider()
    qtbot.addWidget(pydm_slider)

    assert pydm_slider.orientation == Qt.Horizontal
    pydm_slider.orientation = Qt.Vertical
    assert pydm_slider.orientation == Qt.Vertical

    pydm_slider.tickPosition = tick_position
    assert pydm_slider.tickPosition == tick_position
    pydm_slider.num_steps = 5
    assert pydm_slider.num_steps == 5

    pydm_slider.showLimitLabels = show_labels
    assert pydm_slider.showLimitLabels == show_labels

    pydm_slider.showValueLabel = show_labels
    assert pydm_slider.showValueLabel == show_labels

    if show_labels:
        assert pydm_slider.low_lim_label.isVisibleTo(pydm_slider)
        assert pydm_slider.high_lim_label.isVisibleTo(pydm_slider)
        assert pydm_slider.value_label.isVisibleTo(pydm_slider)
    else:
        assert not pydm_slider.low_lim_label.isVisibleTo(pydm_slider)
        assert not pydm_slider.high_lim_label.isVisibleTo(pydm_slider)
        assert not pydm_slider.value_label.isVisibleTo(pydm_slider)


@pytest.mark.parametrize("new_orientation", [
    Qt.Horizontal,
    Qt.Vertical
])
def test_setup_widgets_for_orientation(qtbot, new_orientation):
    """
    Test setting up the slider's orientation.

    Expectations:
    The widget's box layout and margins are correct for the general orientation of the widget.

    Parameters
    ----------
    qtbot : fixture
        pytest-qt window for widget test
    new_orientation : Orientation
        The orientation for the widget.
    """
    pydm_slider = PyDMSlider()
    qtbot.addWidget(pydm_slider)

    pydm_slider.setup_widgets_for_orientation(new_orientation)
    layout = pydm_slider.layout()
    assert layout

    if new_orientation == Qt.Horizontal:
        assert type(layout) == QVBoxLayout
        assert layout.parent() == pydm_slider
        assert layout.contentsMargins() == QMargins(4, 0, 4, 4)
        assert layout.count() == 2

        label_layout = layout.itemAt(0)
        assert type(label_layout) == QHBoxLayout
        assert label_layout.count() == 5
        assert all([label_layout.stretch(i) == 0 for i in range(0, label_layout.count())])
        assert pydm_slider.orientation == new_orientation
    elif new_orientation == Qt.Vertical:
        assert type(layout) == QHBoxLayout
        assert layout.parent() == pydm_slider
        assert layout.contentsMargins() == QMargins(0, 4, 4, 4)
        assert layout.count() == 2

        label_layout = layout.itemAt(0)
        assert type(label_layout) == QVBoxLayout
        assert label_layout.count() == 5
        assert all([label_layout.stretch(i) == 0 for i in range(0, label_layout.count())])
        assert pydm_slider._slider.orientation() == new_orientation


@pytest.mark.parametrize("minimum, maximum, current_value", [
    (10, 20.5, 11),
    (10, 1, 5),
    (10, 20, 30),
    (-10, 20.5, -5),
])
def test_update_labels(qtbot, minimum, maximum, current_value):
    """
    Test the changes in the user minimum, user maximum, and the current value labels as the widget's slider component
    moves.

    Expectations:
    The widget's min, max, and current values are reflected correctly on the correponsiding labels.

    Parameters
    ----------
    qtbot : fixture
        pytest-qt window for widget test
    minimum : int
        The slider's minimum value as set by the user
    maximum : int
        The slider's maximum value as set by the user
    current_value : int
        The current slider's value as set by the user
    """
    def validate(value, widget):
        if value is None:
            assert widget.text() == ""
        else:
            assert widget.text() == str(float(value))

    pydm_slider = PyDMSlider()
    qtbot.addWidget(pydm_slider)

    pydm_slider.userDefinedLimits = True
    pydm_slider.userMinimum = minimum
    pydm_slider.userMaximum = maximum

    pydm_slider.internal_slider_moved(current_value)

    pydm_slider.update_labels()

    validate(minimum, pydm_slider.low_lim_label)
    validate(maximum, pydm_slider.high_lim_label)
    validate(pydm_slider._slider_position_to_value_map[current_value], pydm_slider.value_label)


@pytest.mark.parametrize("minimum, maximum, write_access, connected", [
    (None, None, True, True),
    (None, 10, True, True),
    (10, None, True, True),
    (10, 20, True, True),
    (20, 20, True, True),
    (20, 30, True, True),
    (-10, 20, True, True),
    (10, 20, True, False),
    (10, 20, False, True),
    (10, 20, False, False),
])
def test_reset_slider_limits(qtbot, minimum, maximum, write_access, connected):
    """
    Test the updating of the limits when the silder is reset.

    Expectations:
    The minimum and maximum limits, as well as the slider numeric steps, are updated correctly.

    Parameters
    ----------
    qtbot : fixture
        pytest-qt window for widget test
    minimum : int
        The user-defined minimum value for the slider
    maximum : int
        The user-defined maximum value for the slider
    write_access : bool
        True if the widget has write access to the data channel; False otherwise
    connected : bool
        True if the widget is connected to the data channel; False otherwise
    """
    pydm_slider = PyDMSlider()
    qtbot.addWidget(pydm_slider)

    pydm_slider.userDefinedLimits = True
    pydm_slider.userMinimum = minimum
    pydm_slider.userMaximum = maximum

    pydm_slider.write_access_changed(write_access)

    pydm_slider.connection_changed(connected)

    pydm_slider.reset_slider_limits()

    if minimum is None or maximum is None:
        assert pydm_slider._needs_limit_info is True
    else:
        assert pydm_slider._needs_limit_info is False
        assert pydm_slider.userMinimum == minimum
        assert pydm_slider.userMaximum == maximum
        assert pydm_slider._slider.minimum() == 0
        assert pydm_slider._slider.maximum() == pydm_slider.num_steps - 1
        assert pydm_slider._slider.singleStep() == 1
        assert pydm_slider._slider.pageStep() == 10
        assert np.array_equal(pydm_slider._slider_position_to_value_map,
                              np.linspace(pydm_slider.minimum, pydm_slider.maximum, num=pydm_slider._num_steps))
        assert pydm_slider.isEnabled() == (pydm_slider._write_access and pydm_slider._connected and not \
            pydm_slider._needs_limit_info)


@pytest.mark.parametrize("new_value, minimum, maximum", [
    (10, -10, 20),
    (-10, -10, 20),
    (20, -10, 20),
    (-200, -10, 20),
    (200, -10, 20),
    (0, 0, 0),
    (10, 10, 10),
])
def test_set_slider_to_closest_value(qtbot, new_value, minimum, maximum):
    """
    Test the calculation of the slider's value. Also test set_slider_to_closest_value().

    Expectations:
    Given the user's min and max values, and a value to move the slider to, the new position for the slider must be
    correctly calculated.

    Parameters
    ----------
    qtbot : fixture
        Window for widget testing
    new_value : int
        The new value for the widget
    expected_slider_value : int
        The new calculcated widget value
    """
    pydm_slider = PyDMSlider()
    qtbot.addWidget(pydm_slider)

    pydm_slider.userDefinedLimits = True
    pydm_slider.userMinimum = minimum
    pydm_slider.userMaximum = maximum

    pydm_slider._slider.setValue(0)
    assert pydm_slider._slider.value() == 0

    expected_slider_value = np.argmin(abs(pydm_slider._slider_position_to_value_map - float(new_value)))
    pydm_slider.set_slider_to_closest_value(new_value)

    if new_value is None or pydm_slider._needs_limit_info:
        assert pydm_slider._silder.value() == 0
    else:
        assert pydm_slider._mute_internal_slider_changes is False
        assert pydm_slider._slider.value() == expected_slider_value


@pytest.mark.parametrize("new_channel_value, is_slider_down", [
    (15, False),
    (15, True),
])
def test_value_changed(qtbot, monkeypatch, new_channel_value, is_slider_down):
    """
    Test the updating of the widget's slider component value when the channel value has changed.

    Expectations:
    The widget's text component will display the correct new value, and the widget's slider component will reflect
    the right movement as calculated.

    Parameters
    ----------
    qtbot : fixture
        Window for widget testing
    monkeypatch : fixture
        To override the default behavior of isSliderDown while simulating whether the widget's slider is being held down
        by the user or not
    new_channel_value : int
        The new value coming from the channel
    is_slider_down : bool
        True if the slider is to be simulated as being held down by the user; False otherwise.
    """
    pydm_slider = PyDMSlider()
    qtbot.addWidget(pydm_slider)

    pydm_slider.userDefinedLimits = True
    pydm_slider.userMinimum = 10
    pydm_slider.userMaximum = 100

    pydm_slider._slider.setValue(0)
    assert pydm_slider._slider.value() == 0

    monkeypatch.setattr(QSlider, "isSliderDown", lambda *args: is_slider_down)
    pydm_slider.value_changed(new_channel_value)

    assert pydm_slider.value_label.text() == pydm_slider.format_string.format(pydm_slider.value)
    if not is_slider_down:
        expected_slider_value = np.argmin(abs(pydm_slider._slider_position_to_value_map - float(new_channel_value)))
        assert pydm_slider._slider.value() == expected_slider_value
    else:
        assert pydm_slider._slider.value() == 0


@pytest.mark.parametrize("which_limit, new_limit, user_defined_limits", [
    ("UPPER", 10.5, True),
    ("UPPER", 10.123, False),
    ("LOWER", -10.5, True),
    ("LOWER", -10.123, False),
])
def test_ctrl_limit_changed(qtbot, which_limit, new_limit, user_defined_limits):
    """
    Test the widget's handling of the upper and lower limit changes.

    Expectations:
    The correct limit change will be updated correctly.

    Parameters
    ----------
    qtbot : fixture
        Window for widget testing
    which_limit : str
        Indicator whether this limit to be updated an Upper or Lower limit.
    new_limit : float
        The new value of the limit
    user_defined_limits : bool
        True if the limit is to be defined by the user; False if by the channel.
    """
    pydm_slider = PyDMSlider()
    qtbot.addWidget(pydm_slider)

    pydm_slider.userDefinedLimits = user_defined_limits

    if which_limit == "UPPER":
        pydm_slider.upper_limit_changed(new_limit)
        assert pydm_slider.get_ctrl_limits()[1] == new_limit
    elif which_limit == "LOWER":
        pydm_slider.lower_limit_changed(new_limit)
        assert pydm_slider.get_ctrl_limits()[0] == new_limit


@pytest.mark.parametrize("value, precision, unit, show_unit, expected_format_string", [
    (123, 0, "s", True, "{:.0f} s"),
    (123.456, 3, "mV", True, "{:.3f} mV"),
])
def test_update_format_string(qtbot, value, precision, unit, show_unit, expected_format_string):
    """
    Test the unit conversion by examining the resulted format string.

    Expectations:

    Provided with the value, precision, unit, and the show unit Boolean flag by the user, this function must provide
    the correct format string to format the displayed value for the widget.

    Parameters
    ----------
    qtbot : fixture
        Window for widget testing
    value : int, float, bin, hex, numpy.array
        The value to be converted
    precision : int
        The
    unit : str
        The unit of the new value
    show_units : bool
        True if the value unit is to be displayed. False otherwise
    expected_format_string : str
        The expected format string that will produce the correct displayed value after the conversion
    """
    pydm_slider = PyDMSlider()
    qtbot.addWidget(pydm_slider)

    pydm_slider.value = value
    pydm_slider._unit = unit
    pydm_slider._prec = precision
    pydm_slider.showUnits = show_unit

    pydm_slider.update_format_string()
    assert pydm_slider.format_string == expected_format_string


# --------------------
# NEGATIVE TEST CASES
# --------------------

@pytest.mark.parametrize("new_orientation", [
    -1,
    1000,
    None,
])
def test_setup_widgets_for_orientation_neg(qtbot, caplog, new_orientation):
    """
    Test the widget's handling of invalid orientation values.

    Expectations:
    An invalid orientation code will cause an error to be logged, and a message informing the user about the invalid
    orientation.

    Parameters
    ----------
    qtbot : fixture
        Window for widget testing
    caplog : fixture
        To capture the log messages
    new_orientation : int
        The invalid orientation value
    """
    pydm_slider = PyDMSlider()
    qtbot.addWidget(pydm_slider)

    pydm_slider.setup_widgets_for_orientation(new_orientation)

    for record in caplog.records:
        assert record.levelno == ERROR
    assert "Invalid orientation" in caplog.text