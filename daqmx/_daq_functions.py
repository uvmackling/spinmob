# -*- coding: utf-8 -*-


import numpy   as _n

import _wc_daq_object as _daq_object


def generate_events(procedure=1):
    """
    Generates a list of event objects

    procedure - int, 1 or 2 for choosing different procedures
    """


    if procedure == 1:

        # Turn MOT off
        e01 = do_event(do_line='do0', status=False, time_ms=10.000)

        # Turn camera on and then off
        e02 = do_event(do_line='do4', status=True,  time_ms=9.990)
        e03 = do_event(do_line='do4', status=False, time_ms=700.0)

        # Pulse absorption beam on for MOT imaging
        e04 = do_event(do_line='do2', status=True,  time_ms=10.1)
        e05 = do_event(do_line='do2', status=False, time_ms=10.15)

        # Pulse absorption beam long after the MOT is gone
        # Turn camera on long after the MOT is gone and then off
        e07 = do_event(do_line='do4', status=True,  time_ms=109.990)
        e08 = do_event(do_line='do4', status=False, time_ms=700.0)

        e09 = do_event(do_line='do2', status=True,  time_ms=110.1)
        e10 = do_event(do_line='do2', status=False, time_ms=110.15)

        # Turn MOT on
        e06 = do_event(do_line='do0', status=True,  time_ms=990.00)


        events = [e01, e06, e07, e08, e09, e10]

    else:  # Run procedure number 2 by default

        e05 = do_event(do_line='do6', status=True,  time_ms=3.000, init_state=False)
        e01 = do_event(do_line='do2', status=False, time_ms=5.000, init_state=True)
        e02 = do_event(do_line='do4', status=True,  time_ms=7.000, init_state=False)
        e03 = do_event(do_line='do2', status=True,  time_ms=10.000, init_state=True)

        e04 = do_event(do_line='do4', status=False, time_ms=8.000, init_state=False)
        e06 = do_event(do_line='do6', status=False, time_ms=9.000, init_state=False)



        events = [e01, e02, e03, e04, e05, e06]

    return events






class do_lines():
    """
    Status of daq digital output lines.  Initialize the state of the digital
    output lines with this class.

    binary_value() outputs binary value of the digital output line state.
    """


    parameters  = {}
    debug = False
    __getitem__ = parameters.__getitem__

    parameter_descriptions = {
        'A'
:        ' Watts - my description of A',
        'B':        ' None  - my description of B'
        }

    def __setitem__(self, key, value):
        self.set(key, value)

    def __init__(self, **kwargs):
        """
        Values stand for "digital out 0", "digital out 1" etc. and
        False sets the line to zero, True sets the line to 5 Volts

        kwargs:
        do0_init : Boolean, initial state of digital out channel
        do1_init : Boolean, initial state of digital out channel
        etc...
        """

        # Set initial state of digital output lines by specifying the kwargs.
        if not kwargs.has_key('do0_init') : kwargs['do0_init'] = False  # Set to True for the MOT laser
        if not kwargs.has_key('do1_init') : kwargs['do1_init'] = False
        if not kwargs.has_key('do2_init') : kwargs['do2_init'] = False
        if not kwargs.has_key('do3_init') : kwargs['do3_init'] = False  # Set to True for the magnetic field coils
        if not kwargs.has_key('do4_init') : kwargs['do4_init'] = False
        if not kwargs.has_key('do5_init') : kwargs['do5_init'] = False
        if not kwargs.has_key('do6_init') : kwargs['do6_init'] = False
        if not kwargs.has_key('do7_init') : kwargs['do7_init'] = False

        if self.debug : print "do_lines.__init___ kwargs :", kwargs

        self.set('do0', kwargs['do0_init'])
        self.set('do1', kwargs['do1_init'])
        self.set('do2', kwargs['do2_init'])
        self.set('do3', kwargs['do3_init'])
        self.set('do4', kwargs['do4_init'])
        self.set('do5', kwargs['do5_init'])
        self.set('do6', kwargs['do6_init'])
        self.set('do7', kwargs['do7_init'])



    def __repr__(self):
        return '__repr__'

    def __str__(self):
        return '__str__'


    def binary_value(self):
        """
        Return the binary value to be written to the daq for the do_lines state.
        """
        p = self.parameters

        bin_val = 1*p['do0'] + 2*p['do1'] + 4*p['do2'] + 8*p['do3'] + 16*p['do4'] + 32*p['do5'] + 64*p['do6'] + 128*p['do7']

        return bin_val

    def list_lines(self):
        keys = self.parameters.keys()
        keys.sort()

        print
        for key in keys: print key,'=',self.parameters[key], self.lines_dict(key)
        print


    def set(self, k, value):
        """
        Sets the variable and then updates all of the appropriate dependent variables.

        single quote the 'k' value.
        """
        if self.debug: print "\nset():", k, value

        # k is the key for the key value pairs.
        p = self.parameters      # Do we need these lines anymore????

        # actually set the value
        p[k] = value

        return



    def lines_dict(self, k):
        """
        Dictionary for units and descriptions of variables and functions.
        """

        if   k == "do0"                 :
            units = " - digital out 0"
        elif k == "do1"           :
            units = " - digital out 1"
        elif k == "do2"           :
            units = " - digital out 2"
        elif k == "do3"           :
            units = " - digital out 3"
        elif k == "do4"           :
            units = " - digital out 4"
        elif k == "do5"           :
            units = " - digital out 5"
        elif k == "do6"           :
            units = " - digital out 6"
        elif k == "do7"           :
            units = " - digital out 7"
        else                             :
            units =  " not specified"
        return units



class do_event():
    """
    Class to define a digital output event.  Turning a particular line High or
    Low at a particular time,

    #TODO: describe whatever ini_state is meaningful for in practice.
    includes the initial status of a particular line.


    """

    def __init__(self, do_line='do_0', status=False, time_ms=100., init_state=False):
        """
        Initialize the line

        TODO: Try and change do_line to an int that specifies the line number
        instead of the cumbersome 'do_0', etc.

        Parameters
        ----------
        do_line    : str, name of the line, should be do_0, do_1, through do_7...
        Status     : bool, line status, False=Off, True=On, default(False)
        time_ms    : float, when event occurs in milliseconds, default(100.)
        init_state : bool, initial line status, False=Off, True=On, default(False)

        TODO: Improve digital line names with do_lines object so they integrate nicely

        """

        # name is a utility value, for example 'event4' can be kept track of
        # even if it is not ordered as the 4th event.
        self.name = None

        self.do_line    = do_line
        self.status     = status
        self.time_ms    = time_ms

        # TODO fix this so that time_s can be used.  labRAD types would probably
        # fix this problem.  For now we are eliminating time_s asa  variable
        # to avoid confusion. time_s needs to be udpated whenever time_ms
        # is changed.  We are not going to track two variables that basically
        # give identical information.
        #self.time_s     = self.time_ms/1000.  # Not a value that should be set, time the event occurs in seconds

        self.init_state = init_state

    def __repr__(self):
        return '[' + str(self.do_line) + ' ' + str(self.status) + ' at ' + str(self.time_ms) + ' ms, init_state=' + str(self.init_state) + ']'
    def __str__(self):
        return '[' + str(self.do_line) + ' ' + str(self.status) + ' at ' + str(self.time_ms) + ' ms, init_state=' + str(self.init_state) + ']'



def make_do_data(do_lines, events=[], clock=1e3):
    """
    Make a data array of binary values with appropriate length to satisify
    timing requirements to be returned and then fed into a daq object.do_task

    events   - list of do_event objects
    clock    - hardware clock frequency (kHz), used to be in Hz, but problems with this associated with two event time values.
    do_lines - do_lines class of the initial state of the lines. This forms the first part of the data array

    Assuming we are using 8 digital output channels
    TODO: Make this function more flexible to recieve arbitrary numbers of channels.
    TODO: Make this handle (nicely) events that happen at the same time
    TODO: Make it so that a zero time event doesn't need to be specified.
    TODO: Get the status of all the channels as their initial state.  Make changes
    to this status based on the digital output events that are input

    For this to work smoothly the initial state should be the same as the final
    state from the previous data written to the daq.  This is not essential.
    TODO: Make this not the case.

    """
    debug=False

    if debug: print "\n"
    if debug: print "---------------------------------------------------------"
    if debug: print "make_do_data()"

    # sort the event list from first time to last time
    # TODO: This happens twice I believe, this redundancy is probably good.
    events = sort_events(events)

    # TODO: Should check for identical event times here
    # Track the state of the digital output lines   ... what does this mean?

    # Loop over the events, generates data for daq_object.do_task
    data = _n.array([], dtype='uint32') # empty array for binary data to be sent to the daq
    if debug : print "events :", events

    if debug : print "events[0].time_ms", events[0].time_ms
    # Number of values for a particular event before the next event.

    # Initialize the line state here.
    # This is for the initial state before the first "event" happens, though the initial state is really an event...
    num_vals     = events[0].time_ms * clock
    binary_val   = do_lines.binary_value()  # This sets the initial state, so initialize properly in do_lines, then retrieve this value.
    if debug : print "initialization event binary_val :", binary_val

    binary_array = binary_val * _n.ones(num_vals, dtype='uint32')
    data = _n.concatenate([data, binary_array])
    #time = time + events[0].time_s
    #if debug : print "num_vals : ", num_vals
    #if debug : print "make_do_data"
    #if debug : print "Before for loop data[-1] : ", data[-1]


    if debug : print "clock=", clock
    if debug : print "events[0]=", events[0]
    if debug : print "events[1]=", events[1]
    if debug : print "events[2]=", events[2]

    if debug : print "events[2].time_ms=", events[2].time_ms


    # This loops over all the events
    for kk in xrange(len(events)-1):    # I think the first loop is true because the lines are initialized before this.

        if debug : print "For loop iteration : ", kk


        # TODO: THIS COULD BE THE PROBLEM.  THE LINE HERE!!

        # We want to know how long to keep the lines in the state of the most recent
        # event.  num_vals gives how many total cycles to keep the lines in the
        # given events state.
        # Number of value for the kk_th event before the kk_th+1 event
        num_vals = (events[kk+1].time_ms - events[kk].time_ms) * clock

        if debug : print "Copies of binary value  before the next event: ", num_vals, ", after event:", kk
        if debug : print "events[kk].time_ms=", events[kk].time_ms
        if debug : print "events[kk+1].time_ms=", events[kk+1].time_ms

        # Event status should be fed into the do_lines object, state, to generate a binary value
        status  = events[kk].status
        do_line = events[kk].do_line

        if debug : print "status : ", status
        if debug : print "do_line : ", do_line

        # Change state based on status and do_line to be changed
        do_lines.set(do_line, status)

        # binary value to change to for this event, to be written to data num_vals times.
        binary_val = do_lines.binary_value()
        if debug : print "binary_val=", binary_val

        # Make array of binary values to concatenate to the data array
        if debug : print "make_do_data num_vals=", num_vals
        binary_array = binary_val * _n.ones(num_vals, dtype='uint32')
        data = _n.concatenate([data, binary_array])



    # TODO: get rid of this hack for final event?
    status  = events[-1].status
    do_line = events[-1].do_line

    do_lines.set(do_line, status)
    binary_val = do_lines.binary_value()
    binary_array = binary_val * _n.ones(1, dtype='uint32')
    data = _n.concatenate([data, binary_array])
    if debug : print "Last event data[-1] : ", data[-1]


    if debug: print "---------------------------------------------------------"
    if debug: print "\n"


    return data



def init_do_dict(events):
    """
    Returns a **kwargs dictionary to be fed into do_lines to set the initial state
    of the digital output lines.  This code is essentially another Matlab hack.

    Looks at each event in the list, and then sets a dictionary value for the
    initial state of the corresponding line.


    events - list of do_event objects

    """
    debug = False

    # Loop over all the events setting the kwarg value for each line as you go.
    # Values will be overwritten, so you need to be consistent.

    initDict = {} # Empty dictionary to hold initial state.

    for kk in xrange(len(events)):
        event = events[kk]

        if debug : print "init_do_kwargs() event.init_state :", event.init_state
        if debug : print "init_do_kwargs() event.do_line :", event.do_line


        # Check to see which channel the event is on,
        # Then set the initial state of this line in kwargs

        # Be very careful changing values here.  This wasted half a day.
        if event.do_line == 'do0':
            initDict['do0_init'] = event.init_state
        elif event.do_line == 'do1':
            initDict['do1_init'] = event.init_state
        elif event.do_line == 'do2':
            initDict['do2_init'] = event.init_state
        elif event.do_line == 'do3':
            initDict['do3_init'] = event.init_state
        elif event.do_line == 'do4':
            initDict['do4_init'] = event.init_state
        elif event.do_line == 'do5':
            initDict['do5_init'] = event.init_state
        elif event.do_line == 'do6':
            initDict['do6_init'] = event.init_state
        elif event.do_line == 'do7':
            initDict['do7_init'] = event.init_state

    if debug : print "init_do_kwargs() initDict :", initDict


    return initDict



def output_digital_events(events, **kwargs):
    """
    Sorts by time and then sends a list of do_events to the daq.

    Parameters
    ----------

    events : list of do_event objects

    **kwargs:
    initDict : dictionary holding the initial state of events,
        if not specified then function uses init_do_kwargs()

    TODO: Add initialization of digital output line status, so that some lines
    can start on, etc.  The default right now is for only line do0 to be on.
    Need to probably add an initialization argument to events.

    """
    debug = False

    if debug : print "START of output_digital_events()"
    if debug : print "Before sorting events."
    # sort the events based on time
    events = sort_events(events)
    if debug : print "After sorting events."
    #if debug : print "output_digital_events() events :", events

    # Initialize state of digital output lines
    # kwargs dictionary is generated that holds the initial state value of
    # the digital output lines.
    if not kwargs.has_key('initDict') : kwargs['initDict'] = init_do_dict(events)
    initDict = kwargs['initDict']


    #if debug : print "output_digital_events() initDict :", initDict

    lines = do_lines(**initDict)

    if debug : print "Before make_do_data."
    # TODO: This is the current speed bottleneck for outputting a lot
    # of digital events, e.g. rapidRepeateEvents in Command_Center
    data  = make_do_data(lines, events)
    if debug : print "After make_do_data."


    t = _daq_object.do_task()
    if debug : print "After _daq_object.do_task()"
    t.settings['do_waveforms'] = data
    t.start()
    if debug: print "After t.start()"
    t.wait_and_clean()

    if debug : print "END of output_digital_events()"
    if debug : print "\n"



def pulse_daq(debug=False, save_events=False):
    """
    Function for sending a pulse sequence to the daq.

    debug       - Boolean for debuggin
    save_events - Call save_events function
    """

    events = generate_events()

    if save_events == True:
        save_events(events)

    lines = do_lines()
    data = make_do_data(lines, events)

    if debug==True: print "data[-1] : ", data[-1]

    t = _daq_object.do_task()
    t.settings['do_waveforms'] = data
    t.start()
    t.wait_and_clean()


def pulse_Ch_Hi(do_line='do1', time=300.):
    """
    Pulse specifed line high for specified time.  Turns channel off to start
    automatically, wait 50 ms and then start the pulse

    TODO: Make this work with **kwargs to do_lines() class

    line - 'do0', 'do1', etc.
    time - pulse high duration in milliseconds
    """


    # Make sure line is off before starting
    e01 = do_event(do_line=do_line, status=False, time_ms=1.000)

    initial_on = 51.000

    # Make it high
    e02 = do_event(do_line=do_line, status=True,  time_ms=initial_on)

    time = time + initial_on

    # Make it low
    e03 = do_event(do_line=do_line, status=False, time_ms=time)

    events = [e01, e02, e03]
    events = sort_events(events)

    lines = do_lines()
    data = make_do_data(lines, events)

    t = _daq_object.do_task()
    t.settings['do_waveforms'] = data
    t.start()
    t.wait_and_clean()


def pulse_Ch_Lo(do_line='do1', time=300.):
    """
    Pulse specifed line low for specified time.  Turns channel on to start
    automatically, wait 50 ms and then start the pulse

    TODO: Make this work with **kwargs to do_lines() class

    line - 'do0', 'do1', etc.
    time - pulse low duration in milliseconds
    """


    # Make sure line is high before starting
    e01 = do_event(do_line=do_line, status=True, time_ms=1.000, init_state=True)

    initial_on = 51.000

    # Make it low
    e02 = do_event(do_line=do_line, status=False,  time_ms=initial_on)

    time = time + initial_on

    # Make it high
    e03 = do_event(do_line=do_line, status=True, time_ms=time, init_state=True)

    events = [e01, e02, e03]
    events = sort_events(events)

    lines = do_lines()
    data = make_do_data(lines, events)

    t = _daq_object.do_task()
    t.settings['do_waveforms'] = data
    t.start()
    t.wait_and_clean()


def pulse_Ch_Hi2(do_line='do1', start_time=51.000, time=300.):
    """
    Pulse specifed line high for specified time.  Turns channel on to start
    automatically, wait 50 ms and then start the pulse

    TODO: Make this work with **kwargs to do_lines() class

    Parameters
    ----------
    line: str, 'do0', 'do1', etc.
    start_time: float, pulse start time in milliseconds
    time: float, pulse low duration in milliseconds
    """

    init_state = False

    # Make sure line is high before starting
    e01 = do_event(do_line=do_line, status=False, time_ms=1.000, init_state=init_state)

    initial_on = start_time

    # Make it low
    e02 = do_event(do_line=do_line, status=True,  time_ms=initial_on, init_state=init_state)

    time = time + initial_on

    # Make it high
    e03 = do_event(do_line=do_line, status=False, time_ms=time, init_state=init_state)

    events = [e01, e02, e03]
    events = sort_events(events)

    lines = do_lines()
    data = make_do_data(lines, events)

    t = _daq_object.do_task()
    t.settings['do_waveforms'] = data
    t.start()
    t.wait_and_clean()



def pulse_Ch_HiCustom(do_line='do4', start_time=1.000, time=0.001):
    """
    Pulse channel high for a specified time.  The total time will be under
    2.047 milliseconds to make sure that we are under the total number of 
    samples of 2,047 with a 1 MHz output rate.

    TODO: Make this work with **kwargs to do_lines() class

    Parameters
    ----------
    line: str, 'do0', 'do1', etc.
    start_time: float, pulse start time in milliseconds
    time: float, pulse low duration in milliseconds
    """

    init_state = False

    # Make sure line is high before starting
    e01 = do_event(do_line=do_line, status=False, time_ms=1.000, init_state=init_state)

    initial_on = start_time

    # Make it low
    e02 = do_event(do_line=do_line, status=True,  time_ms=initial_on, init_state=init_state)

    time = time + initial_on

    # Make it high
    e03 = do_event(do_line=do_line, status=False, time_ms=time, init_state=init_state)

    events = [e01, e02, e03]
    events = sort_events(events)

    lines = do_lines()
    data = make_do_data(lines, events)

    t = _daq_object.do_task()
    t.settings['do_waveforms'] = data
    t.start()
    t.wait_and_clean()





def sort_events(events=[]):
    """
    Sort the events from lowest time value to highest time value.  Return
    sorted list.  It sorts whatever list you give it automatically, to, so you
    don't need to specify a return argument

    events - list of do_event objects

    TODO: Eliminate returning the list or eliminate sorting the list given.

    """
    debug = False

    events.sort(key=lambda x: x.time_ms, reverse=False)

    if debug :
        for kk in xrange(len(events)):
            print "event line :", events[kk].do_line
            print "status :", events[kk].status
            print "time_ms =", events[kk].time_ms
            print "\n"

    return events




def add_timeTo_event(event, time_ms):
    """
    Add a time in milliseconds (time_ms) to an event, then return the event
    with the time added.

    event - do_event object
    time_ms - float, the time you want to add to the event in milliseconds

    """

    event.time_ms = event.time_ms + time_ms

    return event



def add_timeTo_events(events, time_ms):
    """
    Add a time in milliseconds (time_ms) to a list of events, then return the
    list of events with the time added.

    events - list of do_event objects
     time_ms - float, the time you want to add to the events in milliseconds

    """

    for kk in xrange(len(events)):

        events[kk] = add_timeTo_event(events[kk], time_ms)


    return events



