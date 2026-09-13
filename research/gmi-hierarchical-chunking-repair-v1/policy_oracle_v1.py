"""Independent stack-machine enumeration of every admitted complete execution."""
from hierarchy_v1 import price


def enumerate_executions(reg, workload, allowed):
    found=[]
    def walk(pending, mask, cost, output, events):
        if not pending:
            found.append((cost+sum(reg.delivery_price(a) for a in output),mask,output,events));return
        t,*tail=pending;tail=tuple(tail)
        if type(t) is tuple:
            _,j=t
            walk(tail,mask|1<<j,cost+price(reg.admission[j]),output,
                 events+(('retain',j,price(reg.admission[j])),));return
        if type(t) is str:
            c=price(reg.costs[reg.primitives.index(t)])
            walk(tail,mask,cost+c,output+t,events+(('primitive',t,c),));return
        if mask & 1<<t:
            c=price(reg.invocation[t])
            # Expand only to audit the output; the supplied compiled-call meter is c.
            stack=list(reg.bodies[t]);symbols=[]
            while stack:
                node=stack.pop(0)
                if type(node) is str:symbols.append(node)
                else:stack[:0]=reg.bodies[node]
            walk(tail,mask,cost+c,output+''.join(symbols),events+(('invoke',t,c),))
        d=price(reg.dispatch[t]);body=reg.bodies[t]
        walk(body+tail,mask,cost+d,output,events+(('expand',t,d),))
        if t in allowed and not mask & 1<<t:
            walk(body+(('store',t),)+tail,mask,cost+d,output,events+(('expand',t,d),))
    walk(tuple(workload),0,0,'',())
    return found
