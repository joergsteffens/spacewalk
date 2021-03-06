<%@ taglib uri="http://rhn.redhat.com/rhn" prefix="rhn" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<%@ taglib uri="http://struts.apache.org/tags-html" prefix="html" %>
<%@ taglib uri="http://struts.apache.org/tags-bean" prefix="bean" %>


<html>
<head>
</head>
<body>
<rhn:toolbar base="h1" icon="header-errata"
	           helpUrl="">
    <bean:message key="errata.publish.toolbar"/> <c:out value="${advisory}" />
  </rhn:toolbar>

  <p><bean:message key="errata.publish.instructions"/></p>
<c:set var="pageList" value="${requestScope.pageList}" />
<form method="post" name="rhn_list" action="/rhn/errata/manage/SelectChannelsSubmit.do">
<rhn:csrf />
<rhn:list pageList="${requestScope.pageList}" noDataText="errata.publish.nochannels">
  <rhn:listdisplay set="${requestScope.set}" hiddenvars="${requestScope.newset}"
                   button="errata.publish.publisherrata">
    <rhn:set value="${current.id}" />
    <rhn:column header="errata.publish.channelname">
        <c:out value="${current.name}"/>
    </rhn:column>

    <rhn:column header="errata.publish.relevantpackages">
      <c:choose>
        <c:when test="${current.relevantPackages > 0}">
            <a href="/network/errata/manage/errata_channel_intersection.pxt?cid=<c:out value="${current.id}"/>&eid=<c:out value="${param.eid}"/>">
            <c:out value="${current.relevantPackages}"/></a>
        </c:when>
        <c:otherwise>
        <c:out value="${current.relevantPackages}"/>
        </c:otherwise>
      </c:choose>
    </rhn:column>

  </rhn:listdisplay>
</rhn:list>
<input type="hidden" name="eid" value="<c:out value="${param.eid}"/>" />
<input type="hidden" name="returnvisit" value="<c:out value="${param.returnvisit}"/>"/>
</form>
</body>
</html>
