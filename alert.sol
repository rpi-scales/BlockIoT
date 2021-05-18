pragma solidity >0.4.16;

contract alert {
    string ipfs_hash;
    address watch_addr;
    string[] the_event;
    string[3] alert;
    uint day;
    string template;
    uint normality;
    uint time_per_day;
    string[3] current; //Times per day(divide number by 12 hrs), days per week(MTF = Monday tuesday friday), weeks per month

    function set_hash(string memory value) public returns (bool) {
        ipfs_hash = value;
        return true;
    }
    function get_hash() public view returns (string memory) {
        return ipfs_hash;
    }

    function set_day(uint _day) public returns (bool) {
        day = _day;
        return true;
    }

    function get_day() public view returns (uint day) {
        return day;
    }

    function set_template(string memory _template) public returns (bool) {
        template = _template;
        return true;
    }

    function get_template() public view returns (string memory template) {
        Base name = Base(watch_addr);
        name.get_template(2);
        return template;
    }

    function set_watch_addr(address _watch_addr) public returns (bool) {
        watch_addr = _watch_addr;
        return true;
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

    function update_alert() public returns (bool) {
        Base name = Base(watch_addr);
        if ((keccak256(abi.encodePacked((name.get_alert(0)))) == (keccak256(abi.encodePacked("-1"))))) {
            the_event.push("GetPreference");
            return true;
        }
        else{
            alert[0] = name.get_alert(0);
            alert[1] = name.get_alert(1);
            alert[2] = name.get_alert(2);
        }
        return false;
    }

    function get_data() public {
        the_event.push("MakeAPICall");
        the_event.push(template);
        if (normality == 0){
            time_per_day_decide();
            the_event.push("PushNotification");
        }

    }

    function time_per_day_decide() public returns (bool){
        Base name = Base(watch_addr);
        time_per_day += 1;
        return true;
    }
}

abstract contract Base {
    function get_alert(uint256 index) public virtual view returns (string memory);
    function get_template(uint256 index) public virtual view returns (string memory);
}