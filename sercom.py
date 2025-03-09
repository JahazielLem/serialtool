import time
import queue
import simplecom



if __name__ == "__main__":
  catwanQueue = queue.Queue()
  catsnifQueue = queue.Queue()
  
  catwanMonitor = simplecom.SerialMonitor("/dev/tty.usbmodem21101", rx_queue=catwanQueue, prompt=False)
  catsnfMonitor = simplecom.SerialMonitor("/dev/tty.usbmodem212401", 921600, catsnifQueue)

  try:
    catwanMonitor.main()
    catsnfMonitor.main()
    while True:
      if not catwanQueue.empty():
        print(f"Catwan: {catwanQueue.get()}")
      if not catsnifQueue.empty():
        print(f"Sniffe: {catsnifQueue.get()}")
      time.sleep(0.1)
  except KeyboardInterrupt:
    catwanMonitor.close()
    catsnfMonitor.close()
