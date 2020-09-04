

class data_template:
    

    def verify_labels(self,label):
        #Get all combination of values.
        list = ["Combo1","Combo2","Combo3"]
        #Create hash for each combo
        
        #Search device dict to see if hash of each combo exists

        #If hash of the combination matches device dict
            
            #Return the config file for the device

            #Check which template the config is using

            #Get the .json file for that template

            #Go the "parameters" section

            #Find the parameter that matches the keys of parameters

            #check if the current data packet is within the min and max. 

            #return True or False based on this
        
        #If hash of the combination does not match device dict

            #return False

    def format_data(self,device_dict):
        #From dict find out what template is present

        #Retrieve the template json file. 

        #Go to presentation key

        #Get the presentation value

        #Run generate_graph program given device_dict and presentation value

    def generate_graph(self,device_dict,presentation_value):
        #Gather list of all timestamps in device dict

        #Gather list of all data values in device_dict

        #Use Matplotlib to generate a line graph 

    def get_template(template):
        #Retrieve template from ipns key. 

sample_config = {
    "characteristics":{
        "first_name":"manan"
        "last_name":"shukla"
        "dob":"01/12/2001"
    }
    "template":"adherence"
    "identifiers":{
        "patient_id":"12d345"
        "medication_id":"678f9"}
    "data":{
        "Pills Taken":"int"
    }
}
label_2 = {"patient_id":"12345","r-wave":"1","s-wave":"4"}

sample_template = {
    "parameters":{
        "adherence":{
            "min":0,
            "max":1
        }
    },
    "presentation":{
        "line"
    }
}