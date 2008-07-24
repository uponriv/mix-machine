from vm_word import Word
from vm_command import cmdList

def cmpa(command, context):
	M = context.mem.get(command.addr() + context.get_reg_index(command.index()).int())
	F = divmod(command.fmt(), 8)
	context.flags["CF"] = cmp(context.regs["A"].int(F), M.int(F))
	return context.get_reg_l().addr() + 1

def cmpx(command, context):
	M = context.mem.get(command.addr() + context.get_reg_index(command.index()).int())
	F = divmod(command.fmt(), 8)
	context.flags["CF"] = cmp(context.regs["X"].int(F), M.int(F))
	return context.get_reg_l().addr() + 1

def cmpi(command, context):
	M = context.mem.get(command.addr() + context.get_reg_index(command.index()).int())
	F = divmod(command.fmt(), 8)
	I = context.get_reg_index(command.code() - 56)
	context.flags["CF"] = cmp(Word(I.addr()).int(F), M.int(F))	# rI: [*,*,*,0,0,0] -> [*,0,0,0,*,*]
	return context.get_reg_l().addr() + 1

cmdList.add_command(56,	-1, cmpa, 1,	"CMPA")
cmdList.add_command(63,	-1, cmpx, 1,	"CMPX")

cmdList.add_command(57,	-1, cmpi, 1,	"CMP1")
cmdList.add_command(58,	-1, cmpi, 1,	"CMP2")
cmdList.add_command(59,	-1, cmpi, 1,	"CMP3")
cmdList.add_command(60,	-1, cmpi, 1,	"CMP4")
cmdList.add_command(61,	-1, cmpi, 1,	"CMP5")
cmdList.add_command(62,	-1, cmpi, 1,	"CMP6")
