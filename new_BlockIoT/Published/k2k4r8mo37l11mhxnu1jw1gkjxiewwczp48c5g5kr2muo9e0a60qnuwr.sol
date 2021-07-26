pragma solidity >0.5.16;

contract k2k4r8mo37l11mhxnu1jw1gkjxiewwczp48c5g5kr2muo9e0a60qnuwr {
    string[3] biometrics; //First name, last name, dob
    string[] api_info; //every odd = key, every even = value. Ex. api_server,medtronic, patient_id,11234
    string config_file; //Same as above. Ex. "Template","adherence",pills taken,compliance
    string ipfs_hash;
    bool consent;
    string[] the_event;
    string[3] alert = ["-1","-1","-1"]; //Times per day(divide number by 12 hrs), days per week(MTF = Monday tuesday friday), weeks per month

    function return_type() public pure returns (string memory) {
        return "register";
    }
    
    function add_biometrics(uint256 index, string memory _data)
        public
        returns (string memory)
    {
        biometrics[index] = _data;
        return _data;
    }

    function get_biometrics(uint256 index) public view returns (string memory) {
        return biometrics[index];
    }

    function add_api_info(string memory value) public returns (bool) {
        api_info.push(value);
        return true;
    }

    function get_api_length() public view returns (uint) {
        return api_info.length;
    }
    
    function get_api_info(uint256 index) public view returns (string memory) {
        return api_info[index];
    }


    function mod_api_info(uint256 index, string memory value)
        public
        returns (bool)
    {
        api_info[index] = value;
        return true;
    }

    function get_config_file() public view returns (string memory) {
        return config_file;
    }

    function set_config_file(string memory _new_config) public returns (bool) {
        config_file = _new_config;
    }

    function set_hash(string memory value) public returns (bool) {
        ipfs_hash = value;
        return true;
    }

    function get_hash() public view returns (string memory) {
        return ipfs_hash;
    }

    function check_consent() public view returns (bool) {
        return consent;
    }

    function set_consent(bool mod) public returns (bool) {
        consent = mod;
        return consent;
    }
    
    function get_event(uint index) public view returns (string memory) {
        return the_event[index];
    }

    function get_event_length() public view returns (uint) {
        return the_event.length;
    }

    function clear_event() public returns (bool) {
        delete the_event;
        return true;
    }
    function control() public returns (bool) {
        if (consent == false){
            the_event.push("GetConsent");
        }
        return true;
    }
}
