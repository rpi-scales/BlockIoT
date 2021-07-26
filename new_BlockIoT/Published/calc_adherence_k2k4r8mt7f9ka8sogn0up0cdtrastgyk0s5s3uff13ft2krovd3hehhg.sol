pragma solidity >0.5.16;

contract calc_adherence_k2k4r8mt7f9ka8sogn0up0cdtrastgyk0s5s3uff13ft2krovd3hehhg {
    string data;
    string ipfs_hash;
    string[] the_event;
    string config_file;
    string physician_pref;
    //Remember all numbers * 100!
    int thirty_average;
    int physician_limit;
    string time;
    string alerttime;

    function return_type() public pure returns (string memory) {
        return "calculator";
    }

    function set_data(string memory _data) public returns (bool) {
        data = _data;
        return true;
    }

    function set_compliance(int average) public returns (bool) {
        thirty_average = average;
        return true;
    }

    function get_compliance() public returns (int) {
        return thirty_average;
    }

    function set_physician_average(int limit) public returns (bool) {
        physician_limit = limit;
        return true;
    }

    function check_alert()public returns (bool) {
        if (thirty_average <= physician_limit){
            the_event.push("SendAlert:Your patient is not compliant!");
        }
        return true;
    }
    
    function get_data() public view returns (string memory) {
        return data;
    }

    function set_time(string memory _time) public returns (bool) {
        time = _time;
        return true;
    }
    function get_time() public view returns (string memory) {
        return time;
    }

    function set_alerttime(string memory _alerttime) public returns (bool) {
        alerttime = _alerttime;
        return true;
    }
    function get_alerttime() public view returns (string memory) {
        return time;
    }

    function get_config_file() public view returns (string memory) {
        return config_file;
    }

    function physician_prefs(string memory pref) public returns (bool) {
        physician_pref = pref;
        return true;
    }
    
    function set_config_file(string memory _new_config) public returns (bool) {
        config_file = _new_config;
        return true;
    }

    function get_event(uint index) public view returns (string memory) {
        return the_event[index];
    }

    function get_event_length() public view returns (uint) {
        return the_event.length;
    }

    function clear_event() public returns (bool) {
        for (uint i = 0; i < the_event.length; i++){
            the_event[i] = "";
        }
        return true;
    }

    function set_hash(string memory value) public returns (bool) {
        ipfs_hash = value;
        return true;
    }
    
    function get_hash() public view returns (string memory) {
        return ipfs_hash;
    }

    function represent() public returns (bool) {
        the_event.push("RepresentData");
        return true;
    }

    function control() public returns (bool){
        the_event.push("ParseAdherence");
        the_event.push("CalculateAdherence");
        return true;
    }
}