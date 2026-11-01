#pragma once
#include "third_party/otto/otto_assets.inc"
#include <cstring>

// Animation state only. All rasters/indexes remain in flash, selected by unsigned
// elapsed time across tick wrap. Hiding pauses phase; repeated cues do not restart.
class OttoPlayer {
public:
    explicit OttoPlayer(uint32_t now) : started_(now) {}
    static unsigned Find(const char* name) {
        if(!name)return 0;
        if(!std::strcmp(name,"smile"))name="happy";
        for(unsigned i=0;i<otto_assets::ExpressionCount;++i)
            if(!std::strcmp(name,otto_assets::Expressions[i].name))return i;
        return 0;
    }
    bool Select(const char* name,uint32_t now,bool restart=false) {
        const unsigned selected=Find(name);
        if(selected==expression_ && !restart)return false;
        expression_=selected;started_=now;if(!visible_)paused_=now;return true;
    }
    void SetVisible(bool visible,uint32_t now) {
        if(visible==visible_)return;
        if(visible)started_+=now-paused_;else paused_=now;
        visible_=visible;
    }
    unsigned ExpressionId() const {return expression_;}
    unsigned FrameNumber(uint32_t now) const {
        return ((visible_?now:paused_)-started_)/otto_assets::FrameDurationMs%
            otto_assets::Expressions[expression_].count;
    }
    unsigned FrameId(uint32_t now) const {
        return otto_assets::FrameIds[otto_assets::Expressions[expression_].first+FrameNumber(now)];
    }
private:
    uint32_t started_,paused_=0;
    unsigned expression_=0;
    bool visible_=true;
};
