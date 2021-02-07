from elasticsearch import Elasticsearch
import uuid
import math,re
from mentee.models import mentor_profile_clicks

class ElasticDB:

    def __init__(self):
        self.es = Elasticsearch("http://localhost:9200/")

    def find_mentor(self,data):
        """

        :param data:
        :return:
        """

        query = {
            "query": {
                "bool": {

                    "must": [
                    ],
                    "filter": [{"term": {"status": 1}}]
                }
            },
            "highlight": {
                "fields": {
                    "one2one_topics": {"type": "plain"},
                    #"skills": {"type": "plain"},
                    "current_designation": {"type": "plain"},
                    "designation": {"type": "plain"},
                    "languages": {"type": "plain"},

                }
            }
        }

        for key in data:

            #if key=="skills" and len(data[key])!=0:
            #    for ski in data[key]:
            #        query["query"]["bool"]["must"].append({"match_phrase": {"skills": ski}})

            if key=="career_profile" and data[key] is not None:
                query["query"]["bool"]["must"].append({"bool": {"should": [{"match_phrase": {"one2one_topics": data[key]}},
                                     {"match_phrase": {"current_designation": data[key]}},
                                     {"intervals": {"designation": {
                                         "match": {"query": data[key], "max_gaps": 0}}}}
                                     ]}})
            if key=="languages" and len(data[key])!=0:
                query["query"]["bool"]["must"].append({"terms": {"languages": data[key]}})

            if key=='exp' and data[key] is not None:
                query["query"]["bool"]["filter"].append({"range": {"industry_exp": {"gte": data[key]}}})

            if key=='min_charge' and data[key] is not None:
                query["query"]["bool"]["filter"].append({"range": {"121_charge": {"gte": data[key]}}})

            if key=='max_charge' and data[key] is not None:
                query["query"]["bool"]["filter"].append({"range": {"121_charge": {"lte": data[key]}}})

        if len(query["query"]["bool"]["must"])==0:
            return None

        response = self.es.search(index='mentors', doc_type='_doc', body=query)

        profiles = []
        for hits in response["hits"]["hits"]:

            # score = hits['_score']
            id_ = hits["_id"]
            company_name = hits["_source"]["current_company"].title()
            desgnation = hits["_source"]["current_designation"].title()
            name = hits["_source"]["name"].title()
            avatar = hits["_source"]["avatar"]
            industry_exp = hits["_source"]["industry_exp"]
            mb_charge = hits["_source"]["121_charge"]

            if "highlight" not in hits:
                continue
            elif "one2one_topics" not in hits["highlight"]:
                continue

            one2one_topics = []
            #if "one2one_topics" in hits["highlight"]:
            for topic in hits["highlight"]["one2one_topics"]:
                  one2one_topics.append(ElasticDB.striphtml(topic))

            view_count = mentor_profile_clicks.objects.filter(mentor_id=id_).values_list(
                'mentee_id').distinct().count()

            profiles.append({"name": name, "id_": id_, "designation": desgnation, "industry_exp": industry_exp,"topics":hits["_source"]["one2one_topics"],
                             "company_name": company_name, "avatar": avatar, "session_names": one2one_topics,
                             "charge": mb_charge,"view_count":view_count})


        return profiles


    def search_mentor_for_student(self, student_details):
            """

            :param student_details:
            :return:
            """

            query = {
                "query": {
                    "bool": {
                        "should": [
                            {"terms": {"designation": student_details["fields"]}},
                            # {"match_phrase": {"college": student_details["College"]}},
                            # {"match_phrase": {"course": student_details["Degree"]}},
                            # {"match_phrase": {"degree": student_details["Course"]}}


                        ],
                        "filter": {"bool":{"should":[]}}
                    }
                },
                "highlight": {
                    "fields": {
                        "one2one_topics": {"type": "plain"},
                        "skills": {"type": "plain"},
                        # "college": {"type": "plain"},
                        "degree": {"type": "plain"},
                        # "course": {"type": "plain"},
                        # "country": {"type": "plain"},
                        # "prof_country": {"type": "plain"}

                    }
                }
            }
            for skill in student_details["Skills"]:
                query["query"]["bool"]["should"].append({"match_phrase": {"skills": skill}})

            for field in student_details["fields"]:
                query["query"]["bool"]["filter"]['bool']['should'].append({"match_phrase": {"one2one_topics": field}})
                query["query"]["bool"]["filter"]['bool']['should'].append({"term": {"status": 1}})

            response = self.es.search(index='mentors', doc_type='_doc', body=query)

            profiles = []
            for hits in response["hits"]["hits"]:

                # score = hits['_score']
                id_ = hits["_id"]
                company_name = hits["_source"]["current_company"].title()
                desgnation = hits["_source"]["current_designation"].title()
                name = hits["_source"]["name"].title()
                avatar = hits["_source"]["avatar"]
                industry_exp = hits["_source"]["industry_exp"]
                mb_charge = hits["_source"]["121_charge"]

                if "highlight" not in hits:
                    continue
                elif "one2one_topics" not in hits["highlight"]:
                    continue

                one2one_topics = []
                for topic in hits["highlight"]["one2one_topics"]:
                    one2one_topics.append(ElasticDB.striphtml(topic))

                view_count = mentor_profile_clicks.objects.filter(mentor_id=id_).values_list(
                    'mentee_id').distinct().count()

                profiles.append({"name": name, "id_": id_, "designation": desgnation, "industry_exp": industry_exp,
                                 "company_name": company_name, "avatar": avatar, "session_names": one2one_topics,
                                 "charge":mb_charge,"view_count":view_count})

            return profiles

    @staticmethod
    def striphtml(data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)

    def search_mentors_for_prof(self, prof_details):
        """

        :param prof_details:
        :return:
        """

        query = {
            "query": {
                "bool": {
                    "should": [
                        {"match_phrase": {"designation": prof_details["CurrentDesignation"]}},
                        # {"match_phrase": {"college": prof_details["College"]}},
                        # {"match_phrase": {"degree": prof_details["Degree"]}},
                        # {"match_phrase": {"company_name": prof_details["CurrentCompany"]}}

                    ],
                    "filter": {"bool":{"should":[]}}
                }
            },
            "highlight": {
                "fields": {
                    "one2one_topics": {"type": "plain"},
                    "skills": {"type": "plain"},
                    # "college": {"type": "plain"},
                    "degree": {"type": "plain"},
                    "designation": {"type": "plain"},

                }
            }
        }

        for skill in prof_details["Skills"]:
            query["query"]["bool"]["should"].append({"match_phrase": {"skills": skill}})

        for field in prof_details["fields"]:
            query["query"]["bool"]["filter"]['bool']['should'].append({"match_phrase": {"one2one_topics": field}})
            query["query"]["bool"]["filter"]['bool']['should'].append({"term": {"status": 1}})
        print(query,"query                                      ")
        response = self.es.search(index='mentors', body=query)

        profiles = []
        for hits in response["hits"]["hits"]:

            # score = hits['_score']
            id_ = hits["_id"]

            company_name = hits["_source"]["current_company"].title()
            designation = hits["_source"]["current_designation"].title()
            name = hits["_source"]["name"].title()
            avatar = hits["_source"]["avatar"]
            industry_exp = hits["_source"]["industry_exp"]
            mb_charge = hits["_source"]["121_charge"]

            if "highlight" not in hits:
                continue
            elif "one2one_topics" not in hits["highlight"]:
                continue

            one2one_topics = []
            for topic in hits["highlight"]["one2one_topics"]:
                one2one_topics.append(ElasticDB.striphtml(topic))

            view_count = mentor_profile_clicks.objects.filter(mentor_id=id_).values_list(
                'mentee_id').distinct().count()
            profiles.append({"name": name, "id_": id_, "designation": designation, "industry_exp": industry_exp,
                             "company_name": company_name, "avatar": avatar,"session_names":one2one_topics,"charge":mb_charge,
                             "view_count":view_count})

        return profiles

    def add_mentor_data(self,mentor_data):
        """

        :param mentor_data:
        :return:
        """

        company = []
        designation = []
        college = []
        degree = []
        course = []
        prof_duration = []
        locations = []
        current_prof = []
        start_year = []
        for prof in mentor_data["professional_details"]:
            if 'duration' in prof:
                prof_duration.append(prof["duration"])
            if 'company_name' in prof:
                company.append(prof["company_name"])
            if 'position' in prof:
                designation.append(prof['position'])
            if 'location' in prof:
                locations.append(prof["location"])
            if 'period' in prof:
                period = prof["period"]
                if period.split("-")[-1].strip()=='present':
                    current_prof.append(prof)
                    st_year = int(period.split("-")[0].split()[-1])
                    start_year.append(st_year)

        current_company = None
        current_designation = None
        if len(current_prof)==1:
            current_company = current_prof[0]["company_name"]
            current_designation = current_prof[0]["position"]
        elif len(current_prof)>1:
            index_max = max(range(len(start_year)), key=start_year.__getitem__)
            current_company = current_prof[index_max]["company_name"]
            current_designation = current_prof[index_max]["position"]

        for edu in mentor_data["educational_details"]:
            if 'institute_name' in edu:
                college.append(edu['institute_name'])
            if 'degree' in edu:
                degree.append(edu['degree'])
            if 'course' in edu:
                course.append(edu['course'])

        industry_exp = None

        def cal_experience(exp_list):
            year = 0
            month = 0
            for i in exp_list:
                yr_list = i.split("yr")
                mo_list = i.split("mo")
                if len(yr_list) > 1:
                    year += int(yr_list[0])
                    mos_list = re.findall(r'\d+', yr_list[1])
                    if len(mos_list) == 1:
                        month += int(mos_list[0])
                elif len(mo_list) > 1:
                    month += int(mo_list[0])
            year += math.floor(month / 12)
            month = month % 12
            return round(year + (month / 12), 1)

        if len(prof_duration) > 0:
            industry_exp = cal_experience(prof_duration)

        doc = {
            "company": company,
            "current_company":current_company,
            "current_designation":current_designation,
            "designation": designation,
            "name":mentor_data["name"],
            "about": mentor_data["about"],
            "avatar":mentor_data["avatar"],
            "company_city": locations,
            "company_country": locations,
            "college": college,
            "degree": degree,
            "course": course,
            'skills': mentor_data["skills"],
            'languages': mentor_data['languages'],
            "status":0,
            "industry_exp":industry_exp
        }
        idd = mentor_data["mentor_id"]
        res = self.es.create(index="mentors", doc_type='_doc',id=idd,body=doc, refresh=True)
        print(res['result'])

        return industry_exp

    def update_mentor_topics_in_es(self,mentor_topics,mentor_id, mb_charge):
        """

        :param mentor_topics:
        :param mentor_id:
        :return:
        """

        self.es.update(index='mentors', id=mentor_id, body={"doc": {"one2one_topics": mentor_topics,
                                                                    "status": 1,"121_charge":mb_charge}})

    def deactivate_mentor_in_es(self, mentor_id):
        """

        :param mentor_id:
        :return:
        """
        self.es.update(index='mentors', id=mentor_id, body={"doc": {"status": 1}})
