pragma solidity >=0.4.16;

contract retrieve {
    string ipfs_hash;
    address watch_addr;
    string[] the_event;
    uint goal_time;
    event GetConsent(uint indexed message);
    event Publish_Data(uint indexed message);
    event start_timer(uint indexed message);
    
    function set_hash(string memory value) public returns (bool) {
        ipfs_hash = value;
        return true;
    }
    function get_hash() public view returns (string memory) {
        return ipfs_hash;
    }
    
    function set_watch_addr(address _watch_addr) public returns (bool) {
        watch_addr = _watch_addr;
        return true;
    }

    function set_time(uint time) public returns (bool) {
        goal_time = time;
        return true;
    }
    
    function get_time() public view returns (uint) {
        return block.timestamp;
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

    function handle_retrieve() public {
        Base name = Base(watch_addr);
        if (name.check_consent() == false){
            the_event.push("GetConsent");
        }
        the_event.push("PublishData");
        the_event.push("SetTimer");
    }
}

abstract contract Base {
    function check_consent() public virtual returns(bool);
}