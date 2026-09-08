"""PID-stable signalling on the registered Linux x86_64 host; no PID kill fallback."""
import ctypes,os,platform,signal
_LIBC=ctypes.CDLL(None,use_errno=True)
def _syscall(number,*args):
 if platform.system()!="Linux" or platform.machine()!="x86_64":
  raise RuntimeError("PIDFD_UNQUALIFIED_PLATFORM")
 result=_LIBC.syscall(ctypes.c_long(number),*[ctypes.c_long(a) for a in args])
 if result<0:
  error=ctypes.get_errno();raise OSError(error,os.strerror(error))
 return result
def open_pid(pid):
 if hasattr(os,"pidfd_open"):return os.pidfd_open(pid,0)
 return _syscall(434,pid,0)
def send(fd,sig):
 if hasattr(signal,"pidfd_send_signal"):return signal.pidfd_send_signal(fd,sig,None,0)
 return _syscall(424,fd,int(sig),0,0)
def preflight():
 fd=open_pid(os.getpid())
 try:send(fd,0)
 finally:os.close(fd)
 return {"mechanism":"Linux pidfd; native Python API or x86_64 syscalls 434/424",
  "platform":platform.platform(),"signal_zero_verified":True}
