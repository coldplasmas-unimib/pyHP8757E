import serial
import threading
import time
from datetime import datetime
import re

WindowTitle = "Alcatel"
FileExt = "alcatel"

class SerialReader:

    @staticmethod
    def error_msg( code ):
        if( code == 0 ): return "mBar"
        if( code == 1 ): return "Underrange"
        if( code == 2 ): return "Overrange"
        if( code == 3 ): return "Sensor error"
        if( code == 5 ): return "No sensor connected"
        return "Unknown error"

    def thread_function(self):
        break_chars = ["\r", "\n"]

        while True:
            if (self.connected):
                line = ""
                while True:
                    line += self.ser.read(1).decode("utf-8")
                    if len(line) == 0 or line[-1] in break_chars:
                        break
                if (len(line) > 1):
                    probes = line.split(',')
                    error_code = 5
                    value = 0.0
                    if( len( probes ) % 2 == 0 ):
                        for i in range( 0, len( probes ), 2 ):
                            if( int( probes[i] ) == 0 ):
                                error_code = 0
                                value = float( probes[ i+1 ][:-5] )
                                break
                            else:
                                error_code = min( error_code, int( probes[i] ) )
                    newData = ( datetime.now(), value, error_code )

                    self.newData.append( newData )
                    self.saver.stream_data( *newData )

            time.sleep(0.1)

    def __init__(self, saver):
        self.connected = False
        self.thread = threading.Thread(target=self.thread_function)
        self.thread.start()
        self.data = []
        self.newData = []
        self.saver = saver

    def connect(self, port):
        self.ser = serial.Serial(baudrate=9600,bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_TWO,rtscts=False,dsrdtr=False,xonxoff=False)
        self.ser.port = port
        self.ser.dtr = False
        self.ser.rts = False
        self.ser.open()

        self.connected = True

    def close(self):
        self.connected = False
        self.ser.close()

    def newData(self):
        return len( self.newData ) > 0

    def flushData( self ):
        self.data = self.data + self.newData
        self.newData = []

    def getAllData(self):
        if( self.newData ):
            self.flushData()
        return self.data

    def getNewData(self):
        toReturn = self.newData[:]
        self.flushData()
        return toReturn

    def getLastData(self):
        if( len( self.newData ) > 0 ):
            return ( self.newData[-1][0], self.newData[-1][1], self.error_msg( self.newData[-1][2] ) )
        if( len( self.data ) > 0 ):
            return ( self.data[-1][0], self.data[-1][1], self.error_msg( self.data[-1][2] ) )
        return ( datetime.now(), 0, "No data" )
    
    def makeDisplayableData(self, data):
        return "\n".join([d[0].strftime('%H:%M:%S') + "\t" + "{:.2e}".format(d[1]) + "\t" + self.error_msg(d[2]) for d in data])
