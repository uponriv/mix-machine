from vm_word import *
from vm_memory import *
from vm_command import cmdList
from vm_events import *
from vm_errors import VMError

#import vm_command_addr
import vm_command_cmp
#import vm_command_io
import vm_command_jump
import vm_command_load
#import vm_command_math
import vm_command_store
import vm_command_other

class VMContextInvalidIndexError(VMError):
	def __init__(self, index):
		self = VMError("Invalid number of index register")
		self.index = index

class VMContext:
	def __init__(self):
		self.regs = {	"A" :	Word(0),
				"X" : 	Word(0),
				"I1" :	Word(0),
				"I2" :	Word(0),
				"I3" :	Word(0),
				"I4" :	Word(0),
				"I5" :	Word(0),
				"I6" :	Word(0),
				"J" : 	Word(0),
				"L" :	Word(0) }
							
		self.flags = {  "OF" : 0,
				"CF" : 0 }
							
		self.mem = Memory()
		self.mem.fill(0)
		
		self.instructions = 0
		
		self.is_halted = False
		
	def reset(self):
		for i in self.regs:
			self.regs[i] = Word(0)
			
		for i in self.flags:
			self.flags[i] = 0
			
		self.mem.fill(0)
		
		self.instructions = 0
		self.is_halted = False
		
	def get_reg_index(self, index):
		if index == 0:
			return Word(0)
		elif index > 0 and index < 7:
			return Word(self.regs["I" + str(index)])
		else:
			raise VMContextInvalidIndexError(index)
		
	def set_reg_index(self, index, value):
		if index > 0 and index < 7:
			self.regs["I" + str(index)] = Word(value)
			return Word(self.regs["I" + str(index)])
		else:
			raise VMContextInvalidIndexError(index)
		
	def get_reg_l(self):
		return self.regs["L"]
	
	def set_reg_l(self, value):
		self.regs["L"] = value
		
	# debug
	def __str__(self):
		regs = ""
		for i in self.regs:
			regs += "\t" + str(i) + ":\t" + str(self.regs[i]) + "\n"
		return "registers: \n" + str(regs) + "\nflags: \t\t" + str(self.flags) + "\ninstructions: \t" + str(self.instructions) + "\nhalted: \t" + str(self.is_halted) + "\n"

class VM:
	def __init__(self):
		self.context = VMContext()
		
	# debug
	def __str__(self):
		return str(context)
		
	def fill_memory(self, mem):
		pass
					
	def dump_memory(self, begin, end):
		pass
		
	
	def trace(self):
		print "--[trace]-----------------------------------------------"
		
		word = CmdWord(self.context.mem.get(self.context.regs["L"].int()))
		code = word.code()
		fmt = word.fmt()
		command = cmdList.get_command(code, fmt)
		
		try:
			jmp = int(command.func(word, self.context))
			self.context.regs["L"] = Word(jmp)
			self.context.instructions += command.time
		except VMHalt:
			self.context.is_halted = True
		
		print str(self.context)
		word = self.context.mem.get(self.context.regs["L"].int())
		print str(word) + ":\t" + str(cmdList.get_command(word.code(), word.fmt()))
		print "--------------------------------------------------------"
	
	def run(self):
		pass
		
	def reset(self):
		pass
	
	def set_brakepoint(self):
		pass
	def remove_brakepoint(self):
		pass
	def remove_all_brakepoints(self):
		pass
	def get_all_breakpoints(self):
		pass
	
vm = VM()

#		Addr	Index	Fmt	Code	# Offset	Asm
mem = [	Word([	1,0,18,	0,	2,	9]),	# 0		
	Word([	1,0,17,	0,	2,	25]),	# 1		
	Word([	1,0,18,	0,	5,	8]),	# 2		
	Word([	1,0,18,	0,	19,	8]),	# 3		
	Word([	1,0,0,	0,	0,	0]),	# 4		
	
	Word([	1,0,0,	0,	0,	0]),	# 5		NOP 
	Word([	1,0,0,	0,	0,	0]),	# 6		NOP 
	Word([	1,0,0,	0,	0,	0]),	# 7		NOP 
	Word([	1,0,0,	0,	0,	0]),	# 8		NOP 
	Word([	1,0,0,	0,	0,	0]),	# 9		NOP 
	
	Word([	1,0,0,	0,	0,	0]),	# 10		NOP 
	Word([	1,0,0,	0,	0,	0]),	# 11		NOP 
	Word([	1,0,0,	0,	0,	0]),	# 12		NOP 
	Word([	1,0,0,	0,	0,	0]),	# 13		NOP 
	Word([	1,0,0,	0,	0,	0]),	# 14		NOP 
	
	Word([	1,0,19,	0,	0,	39]),	# 15		JMP 19
	Word([	1,0,0,	0,	0,	0]),	# 16		NOP 
	Word([	1,10,20,30,	40,	50]),	# 17		NOP 
	Word([	-1,1,2,	3,	4,	5]),	# 18		NOP 
	Word([	1,0,0,	0,	2,	5]),	# 19		HLT
	]

vm.context.mem.set_range(mem, 0)
for i in vm.context.mem.get_range(0, 20):
	print str(i)

while not vm.context.is_halted:
	raw_input()
	vm.trace()
	print vm.context.mem.get(17)