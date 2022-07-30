from cyclonedx.model.bom import Bom,BomMetaData,Property
from cyclonedx.model import LicenseChoice, OrganizationalEntity,OrganizationalContact,Tool
from cyclonedx.model.component import Component
from cyclonedx.parser import BaseParser
import json
import collections.abc

class Key():
    METADATA='metadata'
    COMPONENT = 'component'
    NAME = 'name'
    SUPPLIER = 'supplier'
    TOOLS='tools'
    AUTHORS='authors'
    PROPERTYS='propertys'

def initOrganizationalContact()-> OrganizationalContact:
   return OrganizationalContact(name="NA")
def initComponent()-> Component:
   return Component(name="NA")
def initOrganizationalEntity()-> OrganizationalEntity:
   return OrganizationalEntity(name="NA")




class BomRead(Bom):
    """
    Parser to read a sbom file
    """

    def __init__(self) -> None:
        super().__init__()


    def bom_from_json_file(filename)-> Bom:
        with open(filename,"r") as file: 
            json_data = json.load(file) 
            bom=BomRead.parse(json_data,Bom)
            return bom 

    mapping = {
        Key.METADATA: BomMetaData,
        Key.SUPPLIER: OrganizationalEntity,
        Key.COMPONENT: Component,
        Key.TOOLS: Tool,
        Key.AUTHORS: OrganizationalContact,
        Key.PROPERTYS:Property
    }

    initializer = {
        "<class 'cyclonedx.model.OrganizationalContact'>": initOrganizationalContact,
        "<class 'cyclonedx.model.component.Component'>": initComponent,
        "<class 'cyclonedx.model.OrganizationalEntity'>": initOrganizationalEntity,
    }


    def parse(component_data,targetClass):
        targetType = str(targetClass)
        if targetType in BomRead.initializer:
            targetObj=BomRead.initializer[targetType]()
        else:
            targetObj = targetClass()
        for v in vars(targetObj):
            vs=v.lstrip('_')
            if vs in component_data:
                vs_type=str(type(component_data[vs]))
                if isinstance(component_data[vs],collections.abc.Sequence) and not (vs_type=="<class 'str'>"):
                    # we are processing an array
                    array_result=[]
                    for element in component_data[vs]:
                        if vs in BomRead.mapping:
                            newObj=BomRead.parse(element,BomRead.mapping[vs])
                            array_result.append(newObj)
                        else:
                            array_result.append(element)
                    setattr(targetObj,v,array_result)
       
                else:
                    #single object
                    if vs in BomRead.mapping:
                        newObj=BomRead.parse(component_data[vs],BomRead.mapping[vs])
                        setattr(targetObj,v,newObj)
                    else:
                        setattr(targetObj,v,component_data[vs])
        return targetObj