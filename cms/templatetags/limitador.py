from django.template import Library

register = Library()

def limita_caracteres(cadena, num_caracteres):
#	import pdb;pdb.set_trace()
	return cadena[:num_caracteres] + "..." if cadena.__len__() >num_caracteres else cadena

register.filter(limita_caracteres)