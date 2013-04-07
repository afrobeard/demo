from models import *
import md5
import random

CHANNELS = {"ARY": {"description": "ARY Channel"},
            "MTV": {"description": "MTV Channel"},
            "ABC": {"description": "ABC Channel"}}

#DataStructure Stores Mapping for All Channels
CHANNEL_ID_MAPPING = {}

#Step 1.1: Create Some Dummy Channels
for channelname in CHANNELS:
    channel = Channel.create_channel(channelname, CHANNELS[channelname]["description"])
    cid = channel.get_id()
    CHANNEL_ID_MAPPING[cid] = channelname

SAMPLE_DRAMA_NAMES = ["Mad Men", "The Walking Dead", "Spartacus", "Flashforward", "Lost", "Luther", "Prison Break", "How I met my mother", "The IT Crowd", "24"]
random.shuffle(SAMPLE_DRAMA_NAMES)

#Step 1.2: Verify Dummy Channel Info
for cid in CHANNEL_ID_MAPPING:
    channel = Channel.get_channel_from_id(cid)
    channelConfigObj = CHANNELS[CHANNEL_ID_MAPPING[cid]]
    assert channel.get_name() == CHANNEL_ID_MAPPING[cid], "Channel Name Mismatch"
    assert channel.get_description() == channelConfigObj["description"], "Channel Description Mismatch"

DRAMA_CHANNEL_TUPLES = []

#Make A Drama Counter for later Testing / Reporting
CHANNEL_DRAMA_COUNTER = {}
for key in CHANNEL_ID_MAPPING:
    CHANNEL_DRAMA_COUNTER[key] = {}

#Step 2.1: Create Some Dummy Drama
for drama_name in SAMPLE_DRAMA_NAMES:
    cid = random.choice(CHANNEL_ID_MAPPING.keys())
    name = drama_name
    synopsis = "Synopsis of: %s"%drama_name # Drama Synopsis
    drama = Drama.create_drama(name, synopsis, channel=cid)
    did = drama.get_id()
    DRAMA_CHANNEL_TUPLES.append({"cid": cid, "did": did, "name": drama_name, "synopsis": synopsis})
    #Put Drama in Counts. Blank Counts at the moment
    CHANNEL_DRAMA_COUNTER[cid][did] = 0
    
    
def get_drama_channel_tuple_from_drama_id(did):
    li = filter(lambda x: x["did"] == did,DRAMA_CHANNEL_TUPLES)
    return li[0]

def get_drama_channel_list_from_channel_id(cid):
    li = filter(lambda x: x["cid"] == cid,DRAMA_CHANNEL_TUPLES)
    return li

#Step 2.2: Verify Dummy Drama Info
for entry in DRAMA_CHANNEL_TUPLES:
    did = entry.get("did")
    drama_name = entry.get("name")
    drama_synopsis = entry.get("synopsis")
    cid = entry.get("cid")
    drama = Drama.get_drama_from_id(did)
    assert drama.get_name() == drama_name, "Drama Name Mismatch"
    assert drama.get_synopsis() == drama_synopsis, "Drama ID Mismatch"
    assert drama.get_channel_id() == cid, "Drama / Channel ID Mismatch %s %s"%(drama.get_channel_id(), cid)
    assert drama.get_channel_name() == CHANNEL_ID_MAPPING[cid], "Drama / Channel Name Mismatch"
    assert drama.get_channel_description() == CHANNELS[CHANNEL_ID_MAPPING[cid]]["description"], "Drama / Channel Description Mismatch"

DRAMA_EPISODE_MAP = {}

for entry in DRAMA_CHANNEL_TUPLES:
    did = entry.get("did")
    drama_name = entry.get("name")
    episode_count = int(random.random()*25)
    for i in xrange(episode_count):
        name = "Episode %d , %s"%(i+1, drama_name)
        synopsis = "Synopsis of %s"%name
        encodedvideo = "http://munchkins.com/%s.flv"%(md5.new("name").hexdigest())
        video = Video.create_video(name, encodedvideo, True, synopsis, drama=did)
        vid = video.get_id()
        DRAMA_EPISODE_MAP[vid] = {'name':name, 'encodedvideo':encodedvideo, 'synopsis':synopsis, 'did': did}

for vid in DRAMA_EPISODE_MAP:
    video = Video.get_video_from_id(vid)
    config_video = DRAMA_EPISODE_MAP.get(vid)
    assert config_video["name"] == video.get_name()
    assert config_video["encodedvideo"] == video.get_videolink()
    assert config_video["synopsis"] == video.get_synopsis()
    assert config_video["did"] == video.get_drama_id()

for entry in DRAMA_CHANNEL_TUPLES:
    did = entry.get("did")
    drama = Drama.get_drama_from_id(did)
    print "Drama Name %s Drama Count %d"%(drama.get_name(), drama.get_episode_count())
         

#Step Verify Counts - Channel Per Drama
for channel_id in CHANNEL_DRAMA_COUNTER:
    num_of_dramas_in_channel = len(CHANNEL_DRAMA_COUNTER[channel_id].keys())
    channel = Channel.get_channel_from_id(channel_id)
    assert channel.get_drama_count() == num_of_dramas_in_channel, "Channels per Drama Count Mismatch %s %s"%(channel.get_drama_count(), num_of_dramas_in_channel)

print "Resetting your datastores"

#Video.collection.remove()
#Drama.collection.remove()
#Channel.collection.remove()
