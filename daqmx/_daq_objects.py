# -*- coding: utf-8 -*-

import numpy    as _n
import PyDAQmx  as _mx

from collections import Iterable

buffer_length = 10000
buffer_string = ' '*buffer_length
def strip_buffer(b): return b[0:b.index('\x00')]

debug_enabled = False
def debug(*args): 
    if debug_enabled: 
        for arg in args: 
            print "  ", arg




class task_base:
    
    _handle  = None
    settings = {}
    
    def __init__(self, **kwargs):
        """
        This object provides a command-line interface for a DAQmx task.
        
        kwargs overwrites default self.settings dictionary.
        """

        # overwrite the defaults
        self(**kwargs)

        self._handle = _mx.TaskHandle()

        debug(self.settings)

    def __getitem__(self, key):        
        """
        Returns a setting.
        """        
        return self.settings[key]

    def __setitem__(self, key, value): 
        """
        Sets a setting.
        """
        if key in self.settings.keys(): self.settings[key] = value
        else: 
            print "'"+str(key)+"' is not a valid setting."
            self.print_settings()           
        
    def __call__(self, **kwargs): 
        """
        Modifies settings based on kwargs.
        """
        for key in kwargs.keys(): self[key] = kwargs[key]
    
    def print_settings(self):
        """
        Lists all settings.
        """
        keys = self.settings.keys()
        keys.sort()
        
        print "Settings:"
        for k in keys: print '  ', k, '=', self.settings[k]
    
    has_key = settings.has_key           
               
               
               
class ai_task(task_base):    

    settings = {"ai_task_name"      : "Default AI Task",
                "ai_rate"           : 10000,
                "ai_mode"           : _mx.DAQmx_Val_FiniteSamps,                
                "ai_samples"        : 1000,
                "ai_timeout"        : 1000.0/10000.0 + 3.0,
                
                "ai_clock_source"   : "",
                "ai_clock_edge"     : _mx.DAQmx_Val_Rising,
                "ai_trigger_source" : "please specify ai_trigger_source",
                "ai_trigger_slope"  : _mx.DAQmx_Val_RisingSlope, 

                "ai_channels"          : [],
                "ai_min"               : -10.0,
                "ai_max"               : 10.0,
                "ai_terminal_config"   : _mx.DAQmx_Val_Cfg_Default, # also DAQmx_Val_RSE, NRSE, Diff
                "ai_units"             : _mx.DAQmx_Val_Volts}          
                
                
    
    
                
    def start(self, **kwargs):
        """
        1. Creates a task using settings.
        2. Starts the task.
        3. Fetches data.
        
        You need to call read_and_clean() after start().
        
        kwargs are sent to self() to set parameters.
        """
        
        # update any last-minute settings
        self(**kwargs)
        debug(self.settings)


        # create the task object. This doesn't return an object, because
        # National Instruments. Instead, we have this handle, and we need
        # to be careful about clearing the thing attached to the handle.
        debug("input task handle")        
        _mx.DAQmxClearTask(self._handle)
        _mx.DAQmxCreateTask(self["ai_task_name"], _mx.byref(self._handle))        
        
        # Loop over all the input channels
        debug("input channels")
        for n in range(len(self["ai_channels"])):

            # get the channel-specific attributes            
            name     = self["ai_channels"][n]
            nickname = name.replace("/","")
            debug(name)

            if isinstance(self["ai_terminal_config"], Iterable): 
                  ai_terminal_config = self["ai_terminal_config"][n]
            else: ai_terminal_config = self["ai_terminal_config"]
            
            
            if isinstance(self["ai_min"], Iterable): 
                  ai_min = self["ai_min"][n]
            else: ai_min = self["ai_min"]
            
            if isinstance(self["ai_max"], Iterable): 
                  ai_max = self["ai_max"][n]
            else: ai_max = self["ai_max"]       

            if isinstance(self["ai_units"], Iterable):   
                  ai_units   = self["ai_units"][n]
            else: ai_units   = self["ai_units"]
            
            # add an input channel
            debug(name)
            _mx.DAQmxCreateAIVoltageChan(self._handle, name, nickname, ai_terminal_config, 
                                         ai_min, ai_max, ai_units, "")
        
        # Configure the clock
        debug("input clock")
        _mx.DAQmxCfgSampClkTiming(self._handle, self["ai_clock_source"], self["ai_rate"], 
                                  self["ai_clock_edge"], self["ai_mode"], self["ai_samples"])        

        # get the actual ai_rate           
        ai_rate = _mx.float64()
        _mx.DAQmxGetSampClkRate(self._handle, _mx.byref(ai_rate))
        debug("input actual ai_rate =", ai_rate.value)
        self(ai_rate=ai_rate.value)
        
        # Configure the trigger
        debug("input trigger")
        _mx.DAQmxCfgDigEdgeStartTrig(self._handle, 
                                     self.settings["ai_trigger_source"],
                                     self.settings["ai_trigger_slope"]) 
                                              
        # Start the task!!
        debug("input start")
        _mx.DAQmxStartTask(self._handle)       
        
        
    def read_and_clean(self):
        """
        This should be called after start().
        
        Collects data from the running task, cleans up, then returns the data.
        """
        
        # Fetch the data
        debug("fetch data")
        array_size = self["ai_samples"]*len(self["ai_channels"])
        
        # create the array in which to store the data
        data       = _n.zeros(array_size, dtype=_n.float64)
        bytes_read = _mx.int32()        
        
        # read the data
        debug("_handle", self._handle)
        _mx.DAQmxReadAnalogF64(
            self._handle,                    # handle to the task
            self["ai_samples"],                 # number of samples per channel (-1 => Read ALL in Buffer)
            self["ai_timeout"],                 # timeout (sec)
            _mx.DAQmx_Val_GroupByChannel,    # how to fill the data array
            data,                            # array to fill
            array_size,                      # array size (samples)
            _mx.byref(bytes_read),           # samples per channel actually read
            None)                            # "reserved"
        
        #Organize the data
        data =  _n.split(data, len(self["ai_channels"]))       
        
        
        # cleanup
        debug("clear input task")
        _mx.DAQmxClearTask(self._handle)
        
        return data
        
        
class ao_task(task_base):    

    _handle  = _mx.TaskHandle()
    settings = {"ao_task_name"      : "Default Output Task",
                "ao_mode"           : _mx.DAQmx_Val_FiniteSamps,
                "ao_timeout"        : 10.0,
                
                "ao_channels"       : [],
                "ao_rate"           : 10000,
                "ao_waveforms"      : [],
                "ao_min"           : -10.0,
                "ao_max"            : 10.0,
                "ao_units"          : _mx.DAQmx_Val_Volts,

                "ao_clock_source"   : "",
                "ao_clock_edge"     : _mx.DAQmx_Val_Rising,
                
                "ao_trigger_source" : "please specify ao_trigger_source",
                "ao_trigger_slope"  : _mx.DAQmx_Val_RisingSlope} 
    
    
                
    def start(self, **kwargs):
        """
        1. Creates a task using settings.
        2. Starts the task.
        
        You need to call wait_and_clean() after you start()
        
        kwargs are sent to self() to set parameters.
        """

        self(**kwargs)
        
        # make sure everything that should be a list is a list
        if not isinstance(self["ao_channels"], Iterable): 
            self["ao_channels"]  = [self["ao_channels"]]
        
        # if the first element of the waveform is not an array
        if len(_n.shape(self["ao_waveforms"][0])) < 1: 
            self["ao_waveforms"] = [self["ao_waveforms"]]
        
        # create the task object. This doesn't return an object, because
        # National Instruments. Instead, we have this handle, and we need
        # to be careful about clearing the thing attached to the handle.
        debug("output task handle")        
        _mx.DAQmxClearTask(self._handle)
        _mx.DAQmxCreateTask(self["ao_task_name"], _mx.byref(self._handle))        
        
        # create all the output channels
        debug("output channels")
        
        # this is an array of output data arrays, grouped by channel
        samples = 0
        data    = _n.array([])
        
        # loop over all the channels
        for n in range(len(self["ao_channels"])):

            # get the channel-specific attributes
            name     = self["ao_channels"][n]
            nickname = name.replace("/","")
            
            debug(name)            
            
            if isinstance(self["ao_min"], Iterable): ao_min = self["ao_min"][n]
            else:                                    ao_min = self["ao_min"]
            
            if isinstance(self["ao_max"], Iterable): ao_max = self["ao_max"][n]
            else:                                    ao_max = self["ao_max"]       

            if isinstance(self["ao_units"], Iterable): ao_units = self["ao_units"][n]
            else:                                      ao_units = self["ao_units"]
            
            waveform = self["ao_waveforms"][n]
            
            # add an output channel
            _mx.DAQmxCreateAOVoltageChan(self._handle, name, nickname, 
                                         ao_min, ao_max, ao_units, "")    
                                         
            # add the corresponding output wave to the master data array
            debug ("data", data, "waveform", waveform)
            data = _n.concatenate([data, waveform])            
            
            # Set the samples number to the biggest output array size
            samples = max(len(self["ao_waveforms"][n]), samples)
                     
        
        # Configure the clock
        debug("output clock")
        _mx.DAQmxCfgSampClkTiming(self._handle, self["ao_clock_source"], self["ao_rate"], 
                                  self["ao_clock_edge"], self["ao_mode"], samples)
              
        # update to the actual ao_rate (may be different than what was set)          
        ao_rate = _mx.float64()
        _mx.DAQmxGetSampClkRate(self._handle, _mx.byref(ao_rate))
        debug("output actual ao_rate =", ao_rate.value)
        self(ao_rate=ao_rate.value)
        
        # Configure the trigger
        debug("output trigger")
        _mx.DAQmxCfgDigEdgeStartTrig(self._handle, self["ao_trigger_source"], self["ao_trigger_slope"])
        
        # write the data to the analog outputs (arm it)
        debug("output write", len(data))
        write_success = _mx.int32() 
        _mx.DAQmxWriteAnalogF64(self._handle, samples, False, self["ao_timeout"],
                _mx.DAQmx_Val_GroupByChannel,   # Type of grouping of data in the array (for interleaved use DAQmx_Val_GroupByScanNumber)
                data,                           # Array of data to output
                _mx.byref(write_success),       # Output the number of successful write
                None)                           # Reserved input (just put in None...)
        debug("success:", samples, write_success)    
        
        # Start the task!!
        debug("output start")
        _mx.DAQmxStartTask(self._handle)       
    
    
    def wait_and_clean(self):
        """
        This should be called after start().
        
        Waits for the task to finish and then cleans up.
        """
        
        #Wait for the task to finish
        complete = _mx.bool32()
        while not (complete): _mx.DAQmxGetTaskComplete(self._handle, _mx.byref(complete))        
        
        # cleanup
        debug("clear output task")
        _mx.DAQmxClearTask(self._handle)

        


        
        
class do_task(task_base):    

    _handle  = _mx.TaskHandle()
    settings = {"do_task_name"      : "Default Output Task",
                "do_mode"           : _mx.DAQmx_Val_FiniteSamps,
                "do_timeout"        : 5.0,
                
                "do_channels"       : "/PXI1Slot2/port0/line0:7",        # String for channels, e.g. '/PXI1Slot2/port0/line0'.  For multiple: '/PXI1Slot2/port0/line0:7'
                "do_rate"           : 1000000,   # TODO: Confirm this needs to be an integer, works with "do_clock_source":"Onboardclock"
#                "do_rate"           : 100000,   # 

                "do_waveforms"      : [],       # This needs to be uint32, buffered write requires at least two samples. e.g. 8 bit integers to address 8 digital output channels

#                "do_clock_source"   : "100kHzTimebase",  # Works but buggy at 3 and 4 us d.o. pulses
                "do_clock_source"   : "OnboardClock",  # Alternate value that works for Andrew's DAQ: "/PXI1Slot2/100kHzTimebase"

                "do_clock_edge"     : _mx.DAQmx_Val_Rising,
                
                "do_trigger_source" : "/PXI1Slot2/100kHzTimebase",  # Silly values that work for Andrew's DAQ
                "do_trigger_slope"  : _mx.DAQmx_Val_RisingSlope,
                "do_lineGrouping"   : _mx.DAQmx_Val_ChanForAllLines}    # _mx.DAQmx_Val_ChanForAllLines  or _mx.DAQmx_Val_ChanPerLine
    
    
                
    def start(self, **kwargs):
        """
        1. Creates a task using settings.
        2. Starts the task.
        
        You need to call wait_and_clean() after you start()
        
        kwargs are sent to self() to set parameters.
        """

        self(**kwargs)
        
        # create the task object. This doesn't return an object, because
        # National Instruments. Instead, we have this handle, and we need
        # to be careful about clearing the thing attached to the handle.
        debug("output task handle")        
        clear_task = _mx.DAQmxClearTask(self._handle)
        if debug_enabled : print "clear_task (zero means the task is being cleared) : ", clear_task
        _mx.DAQmxCreateTask(self["do_task_name"], _mx.byref(self._handle))        
        
        # create all the output channels
        debug("output channels")
        lineGrouping = self["do_lineGrouping"]        
        
        samples = 0
        name = self["do_channels"]
        debug(name)     
        nickname     = name.replace("/","")
        #nickname = 'Ralph'
    
        # Create digital output channel, may contain multiple lines
        _mx.DAQmxCreateDOChan(self._handle, name, nickname, lineGrouping)    
                  
        data = self["do_waveforms"]
        samples = len(data) 
        
        if debug_enabled : print "samples =", samples
        
        # Configure the clock
        debug("output clock")
        if debug_enabled : print 'self["do_rate"] : ', self["do_rate"]
        _mx.DAQmxCfgSampClkTiming(self._handle, self["do_clock_source"], self["do_rate"], 
                                  self["do_clock_edge"], self["do_mode"], samples)
                      
        # Configure the trigger
        debug("output trigger")
        _mx.DAQmxCfgDigEdgeStartTrig(self._handle, self["do_trigger_source"], self["do_trigger_slope"])
        
        # write the data to the digital outputs (arm it)
        debug("output write", len(data))
        write_success = _mx.int32() 
        if debug_enabled == True : print "samples : ", samples
        if debug_enabled : print "do_channels : ", self['do_channels']
        if debug_enabled : print "self._handle : ", self._handle
        _mx.DAQmxWriteDigitalU32(self._handle, samples, False, self["do_timeout"],
                _mx.DAQmx_Val_GroupByChannel,   # Type of grouping of data in the array (for interleaved use DAQmx_Val_GroupByScanNumber)
                data,                           # Array of data to output
                _mx.byref(write_success),       # Output the number of successful write
                None)                           # Reserved input (just put in None...)
        debug("success:", samples, write_success)    
        
        # Start the task!!
        debug("output start")
        _mx.DAQmxStartTask(self._handle)       
    
    
    
    def wait_and_clean(self):
        """
        This should be called after start().
        
        Waits for the task to finish and then cleans up.
        """
        
        #Wait for the task to finish
        complete = _mx.bool32()
        while not (complete): _mx.DAQmxGetTaskComplete(self._handle, _mx.byref(complete))        
        
        # cleanup
        debug("clear output task")
        _mx.DAQmxClearTask(self._handle)

    



class daq_system:

    device_names = []
 
    def __init__(self):
        """
        This object's job is to provide a command-line interface for all the
        DAQmx devices on the system.
        """

        # get a names of devices on the system
        self.device_names = self.get_device_names()    
        return
    
    def __getitem__(self, device):
        """
        Accepts either integer or device name. Returns device name.
        """
        if isinstance(device, (int, long)): return self.device_names[device]
        else:                               return device
    
    def get_device_names(self):
        """
        Returns a list of names of DAQ devices present on the system.
        """
        _mx.DAQmxGetSysDevNames(buffer_string, buffer_length)

        # now strip and split this thing to return a names.
        return strip_buffer(buffer_string).split(', ')

    def get_di_channel_names(self, device):
        """
        Returns a list of names of digital input channels/lines on device.  
        Device can be an integer or a string name.
        """
        _mx.DAQmxGetDevDILines(self[device], buffer_string, buffer_length)
        return strip_buffer(buffer_string).split(', ')     

    def get_do_channel_names(self, device):
        """
        Returns a list of names of digital output channels/lines on device.  
        Device can be an integer or a string name.
        """
        _mx.DAQmxGetDevDOLines(self[device], buffer_string, buffer_length)
        return strip_buffer(buffer_string).split(', ')
        
    def get_ai_channel_names(self, device):
        """
        Returns a list of names of analog input channels on device. Device can 
        be an integer or a string name.
        """
        _mx.DAQmxGetDevAIPhysicalChans(self[device], buffer_string, buffer_length)
        return strip_buffer(buffer_string).split(', ')
    
    def get_ao_channel_names(self, device):
        """
        Returns a list of names of analog input channels on device. Device can 
        be an integer or a string name.
        """
        _mx.DAQmxGetDevAOPhysicalChans(self[device], buffer_string, buffer_length)
        return strip_buffer(buffer_string).split(', ')

    def get_terminal_names(self, device):
        """
        Returns a list of terminal names (could be used for triggering). Device 
        can be an integer or a string name.
        """
        _mx.DAQmxGetDevTerminals(self[device], buffer_string, buffer_length)
        return strip_buffer(buffer_string).split(', ')

    def ai_single_device(self, device=0, ai_channels=[0,1,3], ai_time=0.01, **kwargs):
        """
        Performs an on-demand single-shot readout of the specified channels and
        returns the data.
        
        device=0                Which device to use. Can be an index or a 
                                device string.
        ai_channels=[0,1,3]     Which channels to read in (by index). This can
                                be a list or a single number.
        ai_time=0.01            How long to take data (seconds)        
        
        **kwargs are sent to daq_input_task()
        """

        # get a decent trigger name
        ai_trigger_source = "/"+self[device]+"/100kHzTimebase"
        debug(ai_trigger_source)
        
        # if ai_channels is a single element, make it into a list.
        if not isinstance(ai_channels, Iterable): ai_channels = [ai_channels]        
        
        # turn the indices into strings
        ai_channel_names          = self.get_ai_channel_names(device)
        ai_selected_channel_names = []
        for n in range(len(ai_channels)): 
            ai_selected_channel_names.append(ai_channel_names[ai_channels[n]])

        # create the task
        ai = ai_task(ai_trigger_source=ai_trigger_source)
        
        # modify the default task parameters
        ai(ai_channels = ai_selected_channel_names,         # names of channels
           ai_samples  = int(1.0*ai["ai_rate"]*ai_time),    # number of samples
           ai_timeout  = ai_time + 3.0,                     # acquisition time + 3 seconds
           **kwargs)                                        # all the other user variables
        
        # start it!
        ai.start()
        
        # read the result.
        return ai.read_and_clean()

    def ao_single_device(self, device=0, ao_channels=[0,1], ao_waveforms=['sin(t)', 'cos(t)'], ao_time=0.01, autozero=True, **kwargs):
        """
        Performs an on-demand single-shot analog out. 
        
        device=0                Which device to use. Can be an index or a string.
        ao_channels=[0,1]       List of channels to use in (by index). 
        ao_waveforms=[]         List of waveforms to send to ao_channels.

                                Each element can be a string function or data.

                                Constants can be used for the strings, such as 
                                'sin(2*pi*f*t)' so long as pi and f are 
                                supplied as keyword arguments. 
                           
        Example:
            ao_single_device(0, [1], ['sin(a*t)'], 0.1, a=2*3.14)

            will generate the waveform sin(2*3.14*t) for 0.1 seconds on device 0
            channel 1
        
        **kwargs are sent to daq_input_task()
        """

        # get a decent trigger name
        ao_trigger_source = "/"+self[device]+"/100kHzTimebase"
        debug(ao_trigger_source)
        
        debug(ao_waveforms)        
        
        # turn the indices into strings
        ao_channel_names          = self.get_ao_channel_names(device)
        ao_selected_channel_names = []
        for n in range(len(ao_channels)): 
            ao_selected_channel_names.append(ao_channel_names[ao_channels[n]])

        # create the task
        ao = ao_task(ao_trigger_source = ao_trigger_source, 
                     ao_channels       = ao_selected_channel_names)
        
        # update with only the kwargs that already exist
        for key in kwargs.keys(): 
            if ao.has_key(key): ao[key] = kwargs.pop(key)
        debug("remaining kwargs", kwargs)

        # loop over the waveforms and convert functions to 
        for n in range(len(ao_waveforms)):
            if isinstance(ao_waveforms[n], str):
                
                # generate the time array
                kwargs['t'] = _n.linspace(0, ao_time, ao["ao_rate"]*ao_time)
                
                # evaluate the expression
                g = dict(_n.__dict__)
                g.update(kwargs)
                
                debug(ao_waveforms[n])
                ao_waveforms[n] = eval(ao_waveforms[n], g)
        
            # if we're supposed to, set the output to zero
            if autozero: ao_waveforms[n] = _n.concatenate([ao_waveforms[n],[0]])
            
        
        debug(ao_waveforms)        
        
        # set the waveforms
        ao(ao_waveforms=ao_waveforms)
        
        # start it, and wait for it to finish
        ao.start()
        ao.wait_and_clean()


    def ao_ai_single_device(self, device=0, ai_channels=[0,1,3], ai_time=0.01, ao_channels=[0,1], ao_waveforms=['sin(t)', 'cos(t)'], ao_time=0.01, autozero=True, **kwargs):
        """
        Performs an on-demand single-shot analog out. 
        
        device = 0              Which device to use. Can be an index or a string.

        ai_channels  = [1,2,3]  Which input channels to use.
        ai_time      = 0.01     How long to acquire data (seconds).
        
        ao_channels  = [0,1]    List of channels to use in (by index). 
        ao_waveforms = []       List of waveforms to send to ao_channels.

                                Each element can be a string function or data.

                                Constants can be used for the strings, such as 
                                'sin(2*pi*f*t)' so long as pi and f are 
                                supplied as keyword arguments. 
        ao_time = 0.01          How long the output waveforms should last.
                           
        Example:
            ao_single_device(0, [1], ['sin(a*t)'], 0.1, a=2*3.14)

            will generate the waveform sin(2*3.14*t) for 0.1 seconds on device 0
            channel 1
        
        **kwargs are sent to daq_input_task()
        """


        # Create the ao channel

        # get a decent trigger name
        ao_trigger_source = "/"+self[device]+"/100kHzTimebase"
        debug(ao_trigger_source)
        
        debug(ao_waveforms)        
        
        # turn the indices into strings
        ao_channel_names          = self.get_ao_channel_names(device)
        ao_selected_channel_names = []
        for n in range(len(ao_channels)): 
            ao_selected_channel_names.append(ao_channel_names[ao_channels[n]])

        # create the task
        ao = ao_task(ao_trigger_source = ao_trigger_source, 
                     ao_channels       = ao_selected_channel_names)
        
        # update with only the kwargs that already exist
        for key in kwargs.keys(): 
            if ao.has_key(key): ao[key] = kwargs.pop(key)
        debug("remaining kwargs", kwargs)

        # loop over the waveforms and convert functions to 
        for n in range(len(ao_waveforms)):
            if isinstance(ao_waveforms[n], str):
                
                # generate the time array
                kwargs['t'] = _n.linspace(0, ao_time, ao["ao_rate"]*ao_time)
                
                # evaluate the expression
                g = dict(_n.__dict__)
                g.update(kwargs)
                
                debug(ao_waveforms[n])
                ao_waveforms[n] = eval(ao_waveforms[n], g)
        
            # if we're supposed to, set the output to zero
            if autozero: ao_waveforms[n] = _n.concatenate([ao_waveforms[n],[0]])
            
        
        debug(ao_waveforms)        
        
        # set the waveforms
        ao(ao_waveforms=ao_waveforms)
        
        
        
        # now create the input task        
        
        # get a decent trigger name
        ai_trigger_source = "/"+self[device]+"/ao/StartTrigger"
        debug(ai_trigger_source)
        
        # if ai_channels is a single element, make it into a list.
        if not isinstance(ai_channels, Iterable): ai_channels = [ai_channels]        
        
        # turn the indices into strings
        ai_channel_names          = self.get_ai_channel_names(device)
        ai_selected_channel_names = []
        for n in range(len(ai_channels)): 
            ai_selected_channel_names.append(ai_channel_names[ai_channels[n]])

        # create the task
        ai = ai_task(ai_trigger_source=ai_trigger_source)
        
        # modify the default task parameters
        ai(ai_channels = ai_selected_channel_names,         # names of channels
           ai_samples  = int(1.0*ai["ai_rate"]*ai_time),    # number of samples
           ai_timeout  = ai_time + 3.0,                     # acquisition time + 3 seconds
           **kwargs)                                        # all the other user variables
        
        
        
        
        # start it!
        ai.start()
        
        # start it, and wait for it to finish
        ao.start()
    
        # read the result and clear the ai task.
        ai_data = ai.read_and_clean()
        
        # clean up the ao task.
        ao.wait_and_clean()
        
        
        return ai_data


def do_single_value(chan_name='PXI1Slot2/port0/line4', debug=True):
    """
    Function that puts a single channel high.  Need to edit this manual.  
    Mainly for Jack to just run and see that do_task works/look to see if 
    other channels work for him.
    
    chan_name - string of a physical channel, from daq_system.get_do_channel_names
    
    2013-05-15 - Andrew Jayich
    """
    
    t = do_task()

    # Arbitrary task name because default doesn't work out of the box    
    t.settings['do_task_name'] = 'default_do_task1'
    
    # setup the clock
    t.settings['do_clock_source'] = 'OnboardClock'
    t.settings['do_rate']         = 1000000

    t.settings['do_trigger_source'] = '/PXI1Slot2/100kHzTimebase'                       # '/PXI1Slot2/do/StartTrigger'

    # Digital out channel(s).  Change manual as you see fit.  I can't yet
    # get this to work with my second channel: ['PXI1Slot2/port0/line1']
    # find channels with daq_system.do_channels(device)
    t.settings['do_channels'] = chan_name
    
    # Create a waveform for do.  Needs to be at least 2 long for some reason.
    # And the data type is important.
    # Set 1's to zeros to make values low.  I can make this generate nice
    # pulses by feeding a large array of 1's and 0's.
    y1 = _n.zeros(3e5, dtype='uint32')
    y2 = _n.ones(5e5, dtype='uint32')
    y2 = 16*y2
    w = _n.concatenate([y1, y2, y1])
    if debug : "waveform, w: ", w
    t.settings['do_waveforms'] = w

    t.start()
    t.wait_and_clean()

#
#
#debug_enabled=False
#s = daq_system()
#print s.ao_ai_single_device(1)
#
#
#import pyqtgraph as _g
#a = _g.mkQApp()
#p = _g.PlotWidget()
#p.show()
#a.processEvents()
#
#for n in range(0,100):
#    data = s.ao_ai_single_device(1, ai_time=0.01)
#    p.clear()    
#    p.addItem(_g.PlotCurveItem(data[0]-_n.average(data[0]), color=(255,0,0)))
#    p.addItem(_g.PlotCurveItem(data[1]-_n.average(data[1])))
#    p.addItem(_g.PlotCurveItem(data[2]-_n.average(data[2])))
#    a.processEvents()
